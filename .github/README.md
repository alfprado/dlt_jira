# GitHub Actions Workflow - DLT + DBT Pipeline

Workflow simples e otimizado para execução do pipeline de dados DLT + DBT.

## 📁 Estrutura

```
.github/
├── workflows/
│   └── pipeline.yml          # Workflow principal
├── scripts/
│   └── pipeline-utils.sh     # Script utilitário
└── README.md                 # Esta documentação
```

## 🚀 Workflow Principal

### **`pipeline.yml`**
Workflow único que executa:
1. **Extração de dados** com DLT
2. **Transformação** com DBT
3. **Validação** de dados
4. **Testes** de qualidade
5. **Geração** de documentação

### **Triggers**
- **Push** para `main` ou `develop`
- **Pull Request** para `main` ou `develop`
- **Schedule** diário às 2h UTC
- **Manual** via GitHub Actions UI

### **Tipos de Execução**
- `full`: Pipeline completo (padrão)
- `incremental`: Apenas dados incrementais
- `staging-only`: Apenas camada staging
- `marts-only`: Apenas camada marts

## ⚙️ Configuração

### **Secrets Necessários**
Configure no GitHub Settings > Secrets:

```bash
# Jira API
JIRA_SUBDOMAIN=your-subdomain
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token

# PostgreSQL
POSTGRES_USER=dlt_user
POSTGRES_PASSWORD=your-password
POSTGRES_DB=jira_dw
POSTGRES_PORT=5432
```

### **Variáveis de Ambiente**
```bash
PYTHON_VERSION=3.12
POSTGRES_VERSION=15
```

## 🔧 Script Utilitário

### **`pipeline-utils.sh`**
Script com funções essenciais:

```bash
# Verificar PostgreSQL
./.github/scripts/pipeline-utils.sh wait-postgres

# Executar DLT
./.github/scripts/pipeline-utils.sh run-dlt all
./.github/scripts/pipeline-utils.sh run-dlt incremental
./.github/scripts/pipeline-utils.sh run-dlt staging

# Executar DBT
./.github/scripts/pipeline-utils.sh run-dbt run
./.github/scripts/pipeline-utils.sh run-dbt test
./.github/scripts/pipeline-utils.sh run-dbt docs
./.github/scripts/pipeline-utils.sh run-dbt run-staging
./.github/scripts/pipeline-utils.sh run-dbt run-marts

# Verificar dados
./.github/scripts/pipeline-utils.sh verify-data

# Testar dashboards
./.github/scripts/pipeline-utils.sh test-dashboard
```

## 📊 Execução

### **Automática**
- **Push/PR**: Executa automaticamente
- **Schedule**: Executa diariamente às 2h UTC

### **Manual**
```bash
# Via GitHub CLI
gh workflow run pipeline.yml

# Com tipo específico
gh workflow run pipeline.yml -f run_type=incremental
```

### **Local**
```bash
# Executar pipeline completo
./.github/scripts/pipeline-utils.sh wait-postgres
./.github/scripts/pipeline-utils.sh run-dlt all
./.github/scripts/pipeline-utils.sh run-dbt run
./.github/scripts/pipeline-utils.sh run-dbt test
./.github/scripts/pipeline-utils.sh verify-data
./.github/scripts/pipeline-utils.sh test-dashboard
```

## 📈 Monitoramento

### **Status**
- ✅ **Sucesso**: Pipeline executado com sucesso
- ❌ **Falha**: Erro em alguma etapa
- ⚠️ **Aviso**: Execução com warnings

### **Logs**
- Disponíveis na aba "Actions" do GitHub
- Logs detalhados de cada etapa
- Informações de debug em caso de erro

### **Artifacts**
- **dbt-artifacts**: Documentação e relatórios DBT
- **Retenção**: 7 dias

## 🔍 Troubleshooting

### **Problemas Comuns**

#### **1. Falha na Conexão PostgreSQL**
```bash
# Verificar se o serviço está rodando
# Verificar variáveis de ambiente
# Verificar secrets do GitHub
```

#### **2. Falha na API do Jira**
```bash
# Verificar credenciais
# Verificar rate limits
# Verificar conectividade
```

#### **3. Falha nos Testes DBT**
```bash
# Verificar dependências
# Verificar configuração do profiles.yml
# Verificar dados de entrada
```

### **Debug Local**
```bash
# Verificar conectividade
./.github/scripts/pipeline-utils.sh wait-postgres

# Executar passo a passo
./.github/scripts/pipeline-utils.sh run-dlt all
./.github/scripts/pipeline-utils.sh run-dbt run
./.github/scripts/pipeline-utils.sh verify-data
```

## 📚 Recursos

- [GitHub Actions](https://docs.github.com/en/actions)
- [DLT Documentation](https://dlthub.com/docs)
- [DBT Documentation](https://docs.getdbt.com/)

## 🤝 Contribuição

1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Teste localmente
4. Abra um Pull Request

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma issue no GitHub
- Use as discussions do repositório