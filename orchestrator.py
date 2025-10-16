import dlt
import subprocess
import logging
import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class JiraDataPipeline:
    """Pipeline completo de ingestão e transformação de dados do Jira"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dbt_project_dir = "/app/dbt"
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
    def get_dlt_pipeline(self, pipeline_name: str) -> dlt.Pipeline:
        """Cria pipeline dlt configurado"""
        return dlt.pipeline(
            pipeline_name=pipeline_name,
            destination="postgres",
            dataset_name="jira_data",
            progress="log",
            dev_mode=False  # Desabilitar dev_mode para usar schema fixo
        )
    
    def extract_data(self, data_type: str = "all") -> bool:
        """Executa extração de dados usando dlt"""
        logger.info(f"🚀 Iniciando extração de dados: {data_type}")
        
        try:
            pipeline = self.get_dlt_pipeline(f"jira_{data_type}")
            
            if data_type == "all":
                return self._extract_all_data(pipeline)
            elif data_type == "issues":
                return self._extract_issues_only(pipeline)
            elif data_type == "projects":
                return self._extract_projects_only(pipeline)
            elif data_type == "users":
                return self._extract_users_only(pipeline)
            else:
                logger.error(f"Tipo de dados não suportado: {data_type}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro na extração de dados: {e}")
            return False
    
    def _extract_all_data(self, pipeline: dlt.Pipeline) -> bool:
        """Extrai todos os dados do Jira"""
        from jira import jira, jira_search
        
        try:
            # Projetos
            logger.info("📁 Extraindo projetos...")
            projects_resource = jira().projects
            pipeline.run([projects_resource])
            logger.info("✅ Projetos extraídos com sucesso")
            
            # Usuários
            logger.info("👥 Extraindo usuários...")
            users_resource = jira().users
            pipeline.run([users_resource])
            logger.info("✅ Usuários extraídos com sucesso")
            
            # Issues
            logger.info("🎫 Extraindo issues...")
            issues_resource = jira_search().issues(jql_queries=['updated >= "-5d"'])
            pipeline.run([issues_resource])
            logger.info("✅ Issues extraídas com sucesso")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na extração completa: {e}")
            return False
    
    def _extract_issues_only(self, pipeline: dlt.Pipeline) -> bool:
        """Extrai apenas issues"""
        from jira import jira_search
        
        try:
            issues_resource = jira_search().issues(jql_queries=['updated >= "-30d"'])
            pipeline.run([issues_resource])
            logger.info("✅ Issues extraídas com sucesso")
            return True
        except Exception as e:
            logger.error(f"❌ Erro na extração de issues: {e}")
            return False
    
    def _extract_projects_only(self, pipeline: dlt.Pipeline) -> bool:
        """Extrai apenas projetos"""
        from jira import jira
        
        try:
            projects_resource = jira().projects
            pipeline.run([projects_resource])
            logger.info("✅ Projetos extraídos com sucesso")
            return True
        except Exception as e:
            logger.error(f"❌ Erro na extração de projetos: {e}")
            return False
    
    def _extract_users_only(self, pipeline: dlt.Pipeline) -> bool:
        """Extrai apenas usuários"""
        from jira import jira
        
        try:
            users_resource = jira().users
            pipeline.run([users_resource])
            logger.info("✅ Usuários extraídos com sucesso")
            return True
        except Exception as e:
            logger.error(f"❌ Erro na extração de usuários: {e}")
            return False
    
    def transform_data(self, dbt_command: str = "run") -> bool:
        """Executa transformações usando dbt"""
        logger.info(f"🔄 Iniciando transformação de dados: dbt {dbt_command}")
        
        try:
            # Verificar se estamos no diretório correto
            if os.path.exists("/app/dbt"):
                dbt_dir = Path("/app/dbt")  # Docker
            else:
                dbt_dir = Path("/home/alfprado/dev/Flexiana/dlt_jira/dbt")  # Local
                
            if not dbt_dir.exists():
                logger.error(f"❌ Diretório dbt não encontrado: {dbt_dir.absolute()}")
                return False

            # Configurar variáveis de ambiente para dbt
            env = os.environ.copy()
            env["DBT_LOG_PATH"] = "/tmp/dbt_logs"  # Usar diretório temporário com permissões
            
            # Executar dbt diretamente usando os.system
            
            # Mudar para o diretório dbt
            original_cwd = os.getcwd()
            os.chdir(dbt_dir)
            
            try:
                # Executar dbt
                cmd = f"dbt {dbt_command} --log-level info"
                logger.info(f"Executando: {cmd} em {dbt_dir}")
                
                result_code = os.system(cmd)
                
                if result_code == 0:
                    logger.info(f"✅ dbt {dbt_command} executado com sucesso")
                    return True
                else:
                    logger.error(f"❌ dbt {dbt_command} falhou com código {result_code}")
                    return False
                    
            finally:
                # Voltar ao diretório original
                os.chdir(original_cwd)
                
        except subprocess.TimeoutExpired:
            logger.error("❌ dbt timeout - processo demorou mais de 30 minutos")
            return False
        except Exception as e:
            logger.error(f"❌ Erro na execução do dbt: {e}")
            return False
    
    def run_full_pipeline(self, data_type: str = "all", dbt_command: str = "run") -> bool:
        """Executa pipeline completo: extração + transformação"""
        logger.info("🚀 Iniciando pipeline completo de dados do Jira")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        # Etapa 1: Extração
        logger.info("📥 ETAPA 1: EXTRAÇÃO DE DADOS")
        logger.info("-" * 40)
        if not self.extract_data(data_type):
            logger.error("❌ Falha na extração de dados. Abortando pipeline.")
            return False
        
        # Etapa 2: Transformação
        logger.info("\n🔄 ETAPA 2: TRANSFORMAÇÃO DE DADOS")
        logger.info("-" * 40)
        if not self.transform_data(dbt_command):
            logger.error("❌ Falha na transformação de dados.")
            return False
        
        # Resumo final
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 PIPELINE CONCLUÍDO COM SUCESSO!")
        logger.info(f"⏱️  Duração total: {duration}")
        logger.info(f"📊 Dados extraídos: {data_type}")
        logger.info(f"🔄 Transformação: dbt {dbt_command}")
        logger.info("=" * 60)
        
        return True
    
    def run_dbt_only(self, dbt_command: str = "run") -> bool:
        """Executa apenas as transformações dbt (sem extração)"""
        logger.info(f"🔄 Executando apenas dbt {dbt_command}")
        return self.transform_data(dbt_command)
    
    def run_extraction_only(self, data_type: str = "all") -> bool:
        """Executa apenas a extração de dados (sem transformação)"""
        logger.info(f"📥 Executando apenas extração: {data_type}")
        return self.extract_data(data_type)


def main():
    """Função principal para execução via linha de comando"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pipeline de dados do Jira com dbt")
    parser.add_argument("--mode", choices=["full", "extract", "transform"], 
                       default="full", help="Modo de execução")
    parser.add_argument("--data-type", choices=["all", "issues", "projects", "users"], 
                       default="all", help="Tipo de dados para extrair")
    parser.add_argument("--dbt-command", default="run", 
                       help="Comando dbt para executar (run, test, docs, etc.)")
    
    args = parser.parse_args()
    
    # Configuração do pipeline
    config = {
        "pipeline_name": "jira_analytics",
        "destination": "postgres",
        "dataset_name": "jira_data"
    }
    
    # Criar e executar pipeline
    pipeline = JiraDataPipeline(config)
    
    try:
        if args.mode == "full":
            success = pipeline.run_full_pipeline(args.data_type, args.dbt_command)
        elif args.mode == "extract":
            success = pipeline.run_extraction_only(args.data_type)
        elif args.mode == "transform":
            success = pipeline.run_dbt_only(args.dbt_command)
        
        if success:
            logger.info("✅ Pipeline executado com sucesso!")
            sys.exit(0)
        else:
            logger.error("❌ Pipeline falhou!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("⏹️  Pipeline interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
