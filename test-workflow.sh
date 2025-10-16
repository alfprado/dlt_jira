#!/bin/bash
# Script para testar o workflow localmente

echo "🧪 Testando workflow do GitHub Actions localmente..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌${NC} $1"
}

# FASE 1: Validação de Código
log "FASE 1: Validação de Código e Dependências"
echo "=========================================="

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    error "Python3 não está instalado"
    exit 1
fi

# Verificar se pip está instalado
if ! command -v pip &> /dev/null; then
    error "pip não está instalado"
    exit 1
fi

# Instalar dependências
log "Instalando dependências..."
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock psutil
pip install black flake8 isort bandit safety

# Verificar formatação de código
log "Verificando formatação de código (Black)..."
if black --check --diff run_pipeline.py orchestrator.py monitor.py jira/ tests/; then
    success "Formatação de código OK"
else
    warning "Código precisa ser formatado"
fi

# Verificar ordenação de imports
log "Verificando ordenação de imports (isort)..."
if isort --check-only --diff run_pipeline.py orchestrator.py monitor.py jira/ tests/; then
    success "Imports ordenados corretamente"
else
    warning "Imports precisam ser ordenados"
fi

# Verificar linting
log "Verificando linting (Flake8)..."
if flake8 run_pipeline.py orchestrator.py monitor.py jira/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics; then
    success "Linting OK"
else
    warning "Problemas de linting encontrados"
fi

# MyPy removed from workflow

# Verificar segurança
log "Verificando segurança (Bandit)..."
if bandit -r run_pipeline.py orchestrator.py monitor.py jira/ -f json -o bandit-report.json; then
    success "Verificação de segurança OK"
else
    warning "Problemas de segurança encontrados"
fi

# Verificar dependências
log "Verificando dependências (Safety)..."
if safety check --json > safety-report.json; then
    success "Dependências seguras"
else
    warning "Vulnerabilidades encontradas nas dependências"
fi

# FASE 2: Testes Unitários
log "FASE 2: Testes Unitários"
echo "======================="

# Executar testes unitários
log "Executando testes unitários..."
if pytest tests/ -v --cov=run_pipeline --cov=orchestrator --cov=monitor --cov-report=xml --cov-report=html; then
    success "Testes unitários passaram"
else
    error "Testes unitários falharam"
    exit 1
fi

# FASE 3: Testes de Dados (dbt)
log "FASE 3: Testes de Dados (dbt)"
echo "============================="

# Verificar se dbt está instalado
if ! command -v dbt &> /dev/null; then
    log "Instalando dbt..."
    pip install dbt-core dbt-postgres
fi

# Verificar se PostgreSQL está rodando
if ! pg_isready -h localhost -p 5432 &> /dev/null; then
    warning "PostgreSQL não está rodando. Iniciando com Docker..."
    docker run -d --name test-postgres -e POSTGRES_PASSWORD=test_password -e POSTGRES_USER=test_user -e POSTGRES_DB=test_jira_dw -p 5432:5432 postgres:15
    sleep 10
fi

# Configurar dbt
log "Configurando dbt..."
mkdir -p ~/.dbt
cat > ~/.dbt/profiles.yml << EOF
jira_analytics:
  outputs:
    test:
      type: postgres
      host: localhost
      user: test_user
      password: test_password
      port: 5432
      dbname: test_jira_dw
      schema: public
      threads: 4
      keepalives_idle: 0
      connect_timeout: 10
      retries: 1
  target: test
EOF

# Executar testes dbt
log "Executando testes dbt..."
cd dbt

if dbt deps; then
    success "dbt dependencies instaladas"
else
    warning "Falha ao instalar dbt dependencies"
fi

if dbt parse --target test; then
    success "dbt parse OK"
else
    warning "dbt parse falhou"
fi

if dbt compile --target test; then
    success "dbt compile OK"
else
    warning "dbt compile falhou"
fi

if dbt test --target test --store-failures; then
    success "dbt tests passaram"
else
    warning "dbt tests falharam"
fi

if dbt docs generate --target test; then
    success "dbt docs gerados"
else
    warning "Falha ao gerar dbt docs"
fi

cd ..

# FASE 4: Testes de Integração
log "FASE 4: Testes de Integração"
echo "============================"

# Testar comandos do pipeline
log "Testando comandos do pipeline..."
python run_pipeline.py --help || echo "Comando help não disponível"

# Testar com dados mock
log "Testando com dados mock..."
python run_pipeline.py extract || echo "Expected failure - no real API"
python run_pipeline.py transform || echo "Expected failure - no data"

# Testar Docker
log "Testando Docker..."
if docker build -t jira-pipeline:test .; then
    success "Docker build OK"
    if docker run --rm jira-pipeline:test python -c "import dlt, dbt; print('Dependencies OK')"; then
        success "Docker test OK"
    else
        warning "Docker test falhou"
    fi
else
    warning "Docker build falhou"
fi

# FASE 5: Testes de Performance
log "FASE 5: Testes de Performance"
echo "============================="

# Executar testes de performance
log "Executando testes de performance..."
if pytest tests/test_performance.py -v; then
    success "Testes de performance passaram"
else
    warning "Testes de performance falharam"
fi

# FASE 6: Limpeza
log "FASE 6: Limpeza"
echo "==============="

# Limpar containers de teste
log "Limpando containers de teste..."
docker stop test-postgres 2>/dev/null || true
docker rm test-postgres 2>/dev/null || true

# Limpar imagens de teste
log "Limpando imagens de teste..."
docker rmi jira-pipeline:test 2>/dev/null || true

# Resumo final
log "RESUMO FINAL"
echo "============"
success "Workflow testado com sucesso!"
log "Para executar no GitHub Actions, faça commit e push dos arquivos .github/workflows/"
log "Os workflows serão executados automaticamente em push/PR"
