# Jira Analytics Pipeline

A comprehensive data pipeline for extracting, transforming, and analyzing Jira data using dlt (data load tool) and dbt (data build tool). This project provides automated data extraction from Jira APIs, data transformation with dbt, and visualization with Grafana dashboards.

## 🚀 Features

- **Automated Data Extraction**: Extract projects, issues, users, and changelog data from Jira APIs
- **Data Transformation**: Transform raw data into analytics-ready models using dbt
- **Incremental Loading**: Efficient data updates with incremental extraction
- **Data Quality**: Built-in data validation and testing
- **Visualization**: Pre-configured Grafana dashboards for analytics
- **Docker Support**: Containerized deployment with Docker Compose
- **Monitoring**: Comprehensive logging and error handling

## 📊 Analytics Capabilities

### Key Metrics
- **Project Performance**: Completion rates, issue counts, project status
- **Issue Analytics**: Resolution times, overdue items, status transitions
- **Team Performance**: User activity, assignment patterns, workload distribution
- **Time-based Analysis**: Trends, aging reports, velocity metrics

### Data Models
- **Dimensions**: Projects, Users, Time-based dimensions
- **Facts**: Issue details, transitions, user performance metrics
- **Staging**: Raw data processing and cleaning

## 🛠️ Technology Stack

- **dlt**: Data extraction and loading
- **dbt**: Data transformation and modeling
- **PostgreSQL**: Data warehouse
- **Grafana**: Data visualization
- **Docker**: Containerization
- **Python**: Pipeline orchestration

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.8+ (for local development)
- Jira API access (API token required)

## 🚀 Quick Start

### 1. Environment Setup

Create a `.env` file in the project root:

```bash
# Jira Configuration
JIRA_SUBDOMAIN=your-subdomain
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-api-token

# Database Configuration
POSTGRES_USER=dlt_user
POSTGRES_PASSWORD=dlt_password
POSTGRES_DB=jira_dw

# Grafana Configuration
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin
```

### 2. Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# Run the pipeline
docker-compose exec pipeline python run_pipeline.py

# View logs
docker-compose logs -f pipeline
```

### 3. Access Services

- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **PostgreSQL**: localhost:5432
- **Pipeline Logs**: Check container logs or mounted logs directory

## 🔧 Local Development

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd dlt_jira

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env-template .env
# Edit .env with your configuration
```

### Running the Pipeline

```bash
# Full pipeline (extract + transform)
python run_pipeline.py

# Extract data only
python run_pipeline.py extract

# Transform data only
python run_pipeline.py transform

# Run dbt tests
python run_pipeline.py test

# Generate dbt documentation
python run_pipeline.py docs
```

### Advanced Usage

```bash
# Extract specific data types
python orchestrator.py --mode extract --data-type issues
python orchestrator.py --mode extract --data-type projects
python orchestrator.py --mode extract --data-type users

# Run specific dbt commands
python orchestrator.py --mode transform --dbt-command test
python orchestrator.py --mode transform --dbt-command docs generate
```

## 📁 Project Structure

```
dlt_jira/
├── jira/                    # dlt source configuration
├── dbt/                     # dbt project
│   ├── models/
│   │   ├── staging/        # Raw data processing
│   │   └── marts/          # Analytics models
│   └── tests/              # Data quality tests
├── grafana/                 # Dashboard configurations
├── orchestrator.py          # Main pipeline orchestrator
├── run_pipeline.py         # Simplified execution script
├── docker-compose.yml      # Container orchestration
└── requirements.txt        # Python dependencies
```

## 📊 Data Models

### Staging Models
- `stg_jira_issues`: Raw issue data with cleaning
- `stg_jira_projects`: Project information
- `stg_jira_users`: User data
- `stg_jira_changelog`: Issue change history

### Analytics Models
- `dim_projects`: Project dimension with metrics
- `dim_users`: User dimension
- `fct_issues_details`: Issue facts with calculated metrics
- `fct_transitions`: Status transition tracking
- `fct_user_performance`: User performance metrics

## 🔍 Monitoring & Logging

- **Pipeline Logs**: Comprehensive logging with timestamps
- **Data Quality**: Automated dbt tests for data validation
- **Performance**: Resource monitoring and optimization
- **Error Handling**: Graceful error recovery and reporting

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/test_integration.py
python -m pytest tests/test_performance.py

# Run dbt tests
python run_pipeline.py test
```

## 📈 Grafana Dashboards

Pre-configured dashboards include:
- **Projects Overview**: Project status, completion rates, issue counts
- **Issues Details**: Issue metrics, resolution times, overdue items
- **Team Performance**: User activity, workload distribution

## 🔧 Configuration

### dlt Configuration
- Incremental loading for efficient updates
- Automatic schema evolution
- Data type inference and validation

### dbt Configuration
- Materialized tables for performance
- Incremental models for large datasets
- Data quality tests and constraints

## 🚨 Troubleshooting

### Common Issues

1. **Authentication Errors**: Verify Jira API token and subdomain
2. **Database Connection**: Check PostgreSQL service status
3. **Memory Issues**: Adjust Docker memory limits
4. **Data Quality**: Review dbt test results

### Debug Commands

```bash
# Check service status
docker-compose ps

# View service logs
docker-compose logs postgres
docker-compose logs pipeline
docker-compose logs grafana

# Test database connection
docker-compose exec postgres psql -U dlt_user -d jira_dw -c "SELECT 1;"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
- Check the troubleshooting section
- Review logs for error messages
- Create an issue in the repository

## 🔄 Updates

The pipeline supports incremental updates:
- Only new/updated data is extracted
- Efficient processing of large datasets
- Automatic state management
- Configurable update frequencies
