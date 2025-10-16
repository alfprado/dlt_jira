"""
Testes de integração para run_pipeline.py
"""

from unittest.mock import Mock, patch

import pytest

from run_pipeline import main


class TestIntegration:
    """Testes de integração para run_pipeline.py"""

    def test_orchestrator_import(self):
        """Testa se o import do orchestrator funciona"""
        try:
            from run_pipeline import JiraDataPipeline

            assert JiraDataPipeline is not None
        except ImportError as e:
            pytest.fail(f"Falha ao importar JiraDataPipeline: {e}")

    def test_sys_import(self):
        """Testa se o import do sys funciona"""
        try:
            from run_pipeline import sys

            assert sys is not None
        except ImportError as e:
            pytest.fail(f"Falha ao importar sys: {e}")

    def test_main_function_exists(self):
        """Testa se a função main existe"""
        from run_pipeline import main

        assert callable(main)

    def test_main_function_signature(self):
        """Testa assinatura da função main"""
        import inspect

        from run_pipeline import main

        sig = inspect.signature(main)
        assert len(sig.parameters) == 0  # main() não tem parâmetros

    def test_config_structure(self):
        """Testa estrutura da configuração padrão"""
        from run_pipeline import main

        # Verifica se a configuração tem as chaves esperadas
        expected_keys = ["pipeline_name", "destination", "dataset_name"]

        # Mock para capturar a configuração
        with patch("run_pipeline.JiraDataPipeline") as mock_class:
            with patch("sys.argv", ["run_pipeline.py"]):
                with patch("sys.exit"):
                    main()

                    # Verifica se JiraDataPipeline foi chamado
                    assert mock_class.called

                    # Captura os argumentos passados
                    call_args = mock_class.call_args
                    config = call_args[0][0]  # Primeiro argumento posicional

                    # Verifica se todas as chaves esperadas estão presentes
                    for key in expected_keys:
                        assert (
                            key in config
                        ), f"Chave '{key}' não encontrada na configuração"

    def test_command_validation(self):
        """Testa validação de comandos"""
        valid_commands = ["extract", "transform", "test", "docs"]

        for command in valid_commands:
            with patch("run_pipeline.JiraDataPipeline") as mock_class:
                mock_pipeline = Mock()
                mock_pipeline.run_extraction_only.return_value = True
                mock_pipeline.run_dbt_only.return_value = True
                mock_pipeline.run_full_pipeline.return_value = True
                mock_class.return_value = mock_pipeline

                with patch("sys.argv", ["run_pipeline.py", command]):
                    with patch("sys.exit") as mock_exit:
                        main()

                        # Verifica se não houve erro de comando inválido
                        assert mock_exit.called
                        exit_code = mock_exit.call_args[0][0]
                        assert (
                            exit_code == 0
                        ), f"Comando '{command}' falhou com código {exit_code}"
