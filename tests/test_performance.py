"""
Testes de performance para run_pipeline.py
"""
import pytest
import time
from unittest.mock import patch, Mock
from run_pipeline import main

class TestPerformance:
    """Testes de performance para run_pipeline.py"""
    
    def test_command_execution_time(self, mock_pipeline_class, mock_pipeline):
        """Testa tempo de execução dos comandos"""
        commands = ['extract', 'transform', 'test', 'docs']
        
        for command in commands:
            with patch('sys.argv', ['run_pipeline.py', command]):
                with patch('sys.exit'):
                    start_time = time.time()
                    main()
                    execution_time = time.time() - start_time
                    
                    # Verifica se a execução é rápida (menos de 1 segundo)
                    assert execution_time < 1.0, f"Comando {command} muito lento: {execution_time}s"
    
    def test_memory_usage(self, mock_pipeline_class, mock_pipeline):
        """Testa uso de memória"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss
            
            with patch('sys.argv', ['run_pipeline.py', 'extract']):
                with patch('sys.exit'):
                    main()
            
            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory
            
            # Verifica se o aumento de memória é razoável (menos de 10MB)
            assert memory_increase < 10 * 1024 * 1024, f"Uso excessivo de memória: {memory_increase} bytes"
        except ImportError:
            pytest.skip("psutil não disponível para teste de memória")
    
    def test_concurrent_execution(self, mock_pipeline_class, mock_pipeline):
        """Testa execução concorrente de comandos"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def run_command(command):
            with patch('sys.argv', ['run_pipeline.py', command]):
                with patch('sys.exit'):
                    start_time = time.time()
                    main()
                    execution_time = time.time() - start_time
                    results.put((command, execution_time))
        
        # Executa comandos em paralelo
        threads = []
        commands = ['extract', 'transform', 'test', 'docs']
        
        for command in commands:
            thread = threading.Thread(target=run_command, args=(command,))
            threads.append(thread)
            thread.start()
        
        # Aguarda todos os threads terminarem
        for thread in threads:
            thread.join()
        
        # Verifica resultados
        while not results.empty():
            command, execution_time = results.get()
            assert execution_time < 1.0, f"Comando {command} muito lento em execução concorrente: {execution_time}s"
    
    def test_large_argument_handling(self, mock_pipeline_class, mock_pipeline):
        """Testa tratamento de argumentos grandes"""
        # Simula argumentos muito grandes
        large_args = ['run_pipeline.py', 'extract'] + ['arg'] * 1000
        
        with patch('sys.argv', large_args):
            with patch('sys.exit'):
                start_time = time.time()
                main()
                execution_time = time.time() - start_time
                
                # Verifica se ainda é rápido mesmo com muitos argumentos
                assert execution_time < 1.0, f"Execução muito lenta com muitos argumentos: {execution_time}s"
