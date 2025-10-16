"""
Testes unitários fundamentais para run_pipeline.py
"""
import pytest
import sys
from unittest.mock import Mock, patch, call
from run_pipeline import main

class TestRunPipeline:
    """Testes unitários para run_pipeline.py"""
    
    def test_default_config_creation(self, mock_pipeline_class, mock_pipeline, mock_sys_exit):
        """Testa se a configuração padrão é criada corretamente"""
        with patch('sys.argv', ['run_pipeline.py']):
            main()
            
            # Verifica se JiraDataPipeline foi chamado com a configuração correta
            expected_config = {
                "pipeline_name": "jira_analytics",
                "destination": "postgres",
                "dataset_name": "jira_data"
            }
            mock_pipeline_class.assert_called_once_with(expected_config)
    
    def test_extract_command_success(self, mock_pipeline_class, mock_pipeline, mock_sys_exit):
        """Testa execução bem-sucedida do comando extract"""
        with patch('sys.argv', ['run_pipeline.py', 'extract']):
            main()
            
            # Verifica se o método correto foi chamado
            mock_pipeline.run_extraction_only.assert_called_once_with("all")
            mock_sys_exit.assert_called_once_with(0)
    
    def test_transform_command_success(self, mock_pipeline_class, mock_pipeline, mock_sys_exit):
        """Testa execução bem-sucedida do comando transform"""
        with patch('sys.argv', ['run_pipeline.py', 'transform']):
            main()
            
            mock_pipeline.run_dbt_only.assert_called_once_with("run")
            mock_sys_exit.assert_called_once_with(0)
    
    def test_test_command_success(self, mock_pipeline_class, mock_pipeline, mock_sys_exit):
        """Testa execução bem-sucedida do comando test"""
        with patch('sys.argv', ['run_pipeline.py', 'test']):
            main()
            
            mock_pipeline.run_dbt_only.assert_called_once_with("test")
            mock_sys_exit.assert_called_once_with(0)
    
    def test_docs_command_success(self, mock_pipeline_class, mock_pipeline, mock_sys_exit):
        """Testa execução bem-sucedida do comando docs"""
        with patch('sys.argv', ['run_pipeline.py', 'docs']):
            main()
            
            mock_pipeline.run_dbt_only.assert_called_once_with("docs generate")
            mock_sys_exit.assert_called_once_with(0)
    
    def test_full_pipeline_execution(self, mock_pipeline_class, mock_pipeline, mock_sys_exit):
        """Testa execução do pipeline completo sem argumentos"""
        with patch('sys.argv', ['run_pipeline.py']):
            main()
            
            mock_pipeline.run_full_pipeline.assert_called_once_with("all", "run")
            mock_sys_exit.assert_called_once_with(0)
    
    def test_invalid_command(self, mock_pipeline_class, mock_pipeline, mock_sys_exit):
        """Testa tratamento de comando inválido"""
        with patch('sys.argv', ['run_pipeline.py', 'invalid']):
            main()
            
            # Verifica se nenhum método do pipeline foi chamado
            mock_pipeline.run_extraction_only.assert_not_called()
            mock_pipeline.run_dbt_only.assert_not_called()
            mock_pipeline.run_full_pipeline.assert_not_called()
            
            # Verifica se exit foi chamado com código de erro (pode ser chamado 2 vezes)
            assert mock_sys_exit.call_count >= 1
            assert 1 in [call[0][0] for call in mock_sys_exit.call_args_list]
    
    def test_extract_command_failure(self, mock_pipeline_class, mock_pipeline, mock_sys_exit):
        """Testa falha na execução do comando extract"""
        mock_pipeline.run_extraction_only.return_value = False
        
        with patch('sys.argv', ['run_pipeline.py', 'extract']):
            main()
            
            mock_pipeline.run_extraction_only.assert_called_once_with("all")
            mock_sys_exit.assert_called_once_with(1)
    
    def test_transform_command_failure(self, mock_pipeline_class, mock_pipeline, mock_sys_exit):
        """Testa falha na execução do comando transform"""
        mock_pipeline.run_dbt_only.return_value = False
        
        with patch('sys.argv', ['run_pipeline.py', 'transform']):
            main()
            
            mock_pipeline.run_dbt_only.assert_called_once_with("run")
            mock_sys_exit.assert_called_once_with(1)
    
    def test_full_pipeline_failure(self, mock_pipeline_class, mock_pipeline, mock_sys_exit):
        """Testa falha na execução do pipeline completo"""
        mock_pipeline.run_full_pipeline.return_value = False
        
        with patch('sys.argv', ['run_pipeline.py']):
            main()
            
            mock_pipeline.run_full_pipeline.assert_called_once_with("all", "run")
            mock_sys_exit.assert_called_once_with(1)
    
    def test_case_insensitive_commands(self, mock_pipeline_class, mock_pipeline, mock_sys_exit):
        """Testa comandos case-insensitive"""
        test_cases = [
            ('EXTRACT', 'run_extraction_only'),
            ('Transform', 'run_dbt_only'),
            ('TEST', 'run_dbt_only'),
            ('DOCS', 'run_dbt_only')
        ]
        
        for command, expected_method in test_cases:
            # Reset mocks for each test case
            mock_pipeline.reset_mock()
            mock_sys_exit.reset_mock()
            
            with patch('sys.argv', ['run_pipeline.py', command]):
                main()
                
                if expected_method == 'run_extraction_only':
                    mock_pipeline.run_extraction_only.assert_called_with("all")
                else:
                    mock_pipeline.run_dbt_only.assert_called()
                
                mock_sys_exit.assert_called_with(0)
    
    def test_multiple_arguments_ignored(self, mock_pipeline_class, mock_pipeline, mock_sys_exit):
        """Testa se argumentos extras são ignorados"""
        with patch('sys.argv', ['run_pipeline.py', 'extract', 'extra', 'args']):
            main()
            
            # Apenas o primeiro argumento deve ser processado
            mock_pipeline.run_extraction_only.assert_called_once_with("all")
            mock_sys_exit.assert_called_once_with(0)
    
    def test_empty_command(self, mock_pipeline_class, mock_pipeline, mock_sys_exit):
        """Testa comando vazio"""
        with patch('sys.argv', ['run_pipeline.py', '']):
            main()
            
            # Comando vazio é tratado como comando inválido
            mock_pipeline.run_extraction_only.assert_not_called()
            mock_pipeline.run_dbt_only.assert_not_called()
            mock_pipeline.run_full_pipeline.assert_not_called()
            
            # Verifica se exit foi chamado com código de erro
            assert mock_sys_exit.call_count >= 1
            assert 1 in [call[0][0] for call in mock_sys_exit.call_args_list]
