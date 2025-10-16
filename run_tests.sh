#!/bin/bash
# Script para executar testes unitários do run_pipeline.py

echo "🧪 Executando testes unitários para run_pipeline.py..."

# Verificar se pytest está instalado
if ! command -v pytest &> /dev/null; then
    echo "📦 Instalando dependências de teste..."
    pip install pytest pytest-cov pytest-mock psutil
fi

# Executar testes
echo "🚀 Executando testes..."
pytest tests/ -v --cov=run_pipeline --cov-report=html --cov-report=term-missing

# Verificar se os testes passaram
if [ $? -eq 0 ]; then
    echo "✅ Todos os testes passaram!"
    echo "📊 Relatório de cobertura gerado em htmlcov/index.html"
else
    echo "❌ Alguns testes falharam!"
    exit 1
fi
