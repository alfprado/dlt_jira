#!/usr/bin/env python3
"""
Script simplificado para executar o pipeline de dados do Jira
"""

import sys
from orchestrator import JiraDataPipeline

def main():
    """Executa o pipeline com configurações padrão"""
    
    # Configuração do pipeline
    config = {
        "pipeline_name": "jira_analytics",
        "destination": "postgres",
        "dataset_name": "jira_data"
    }
    
    # Criar pipeline
    pipeline = JiraDataPipeline(config)
    
    # Verificar argumentos da linha de comando
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "extract":
            print("📥 Executando apenas extração de dados...")
            success = pipeline.run_extraction_only("all")
        elif command == "transform":
            print("🔄 Executando apenas transformação dbt...")
            success = pipeline.run_dbt_only("run")
        elif command == "test":
            print("🧪 Executando testes dbt...")
            success = pipeline.run_dbt_only("test")
        elif command == "docs":
            print("📚 Gerando documentação dbt...")
            success = pipeline.run_dbt_only("docs generate")
        else:
            print(f"Comando não reconhecido: {command}")
            print("Comandos disponíveis: extract, transform, test, docs")
            sys.exit(1)
    else:
        # Executar pipeline completo por padrão
        print("🚀 Executando pipeline completo...")
        success = pipeline.run_full_pipeline("all", "run")
    
    if success:
        print("✅ Pipeline executado com sucesso!")
        sys.exit(0)
    else:
        print("❌ Pipeline falhou!")
        sys.exit(1)

if __name__ == "__main__":
    main()
