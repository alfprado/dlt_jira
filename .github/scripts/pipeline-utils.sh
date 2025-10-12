#!/bin/bash

# Simple Pipeline Utilities
# Essential functions for DLT + DBT pipeline

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Wait for PostgreSQL
wait_for_postgres() {
    local max_attempts=30
    local attempt=1
    
    log_info "Waiting for PostgreSQL..."
    
    while [ $attempt -le $max_attempts ]; do
        if pg_isready -h localhost -p 5432 -U $POSTGRES_USER >/dev/null 2>&1; then
            log_success "PostgreSQL is ready!"
            return 0
        fi
        
        log_info "Attempt $attempt/$max_attempts..."
        sleep 2
        ((attempt++))
    done
    
    log_error "PostgreSQL failed to start"
    return 1
}

# Run DLT pipeline
run_dlt() {
    local run_type=${1:-"all"}
    
    log_info "Running DLT pipeline: $run_type"
    
    case $run_type in
        "incremental")
            python jira_pipeline.py incremental
            ;;
        "staging")
            python jira_pipeline.py staging
            ;;
        "all")
            python jira_pipeline.py all
            ;;
        *)
            log_error "Invalid DLT run type: $run_type"
            return 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        log_success "DLT pipeline completed"
        return 0
    else
        log_error "DLT pipeline failed"
        return 1
    fi
}

# Run DBT commands
run_dbt() {
    local command=$1
    local working_dir=${2:-"dbt"}
    
    log_info "Running DBT: $command"
    
    cd "$working_dir"
    
    case $command in
        "deps")
            dbt deps --profiles-dir .
            ;;
        "run")
            dbt run --profiles-dir .
            ;;
        "test")
            dbt test --profiles-dir .
            ;;
        "docs")
            dbt docs generate --profiles-dir .
            ;;
        "run-staging")
            dbt run --select staging --profiles-dir .
            ;;
        "run-marts")
            dbt run --select marts --profiles-dir .
            ;;
        *)
            log_error "Invalid DBT command: $command"
            return 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        log_success "DBT command completed"
        return 0
    else
        log_error "DBT command failed"
        return 1
    fi
}

# Verify data
verify_data() {
    log_info "Verifying data..."
    
    python3 -c "
import psycopg2
import sys

try:
    conn = psycopg2.connect(
        host='$POSTGRES_HOST',
        port='$POSTGRES_PORT',
        user='$POSTGRES_USER',
        password='$POSTGRES_PASSWORD',
        database='$POSTGRES_DB'
    )
    cur = conn.cursor()
    
    # Check raw data
    cur.execute('SELECT COUNT(*) FROM jira_data.issues;')
    issues_count = cur.fetchone()[0]
    print(f'📊 Raw issues: {issues_count}')
    
    # Check processed data
    cur.execute('SELECT COUNT(*) FROM jira_analytics.fct_issues_details;')
    fact_issues = cur.fetchone()[0]
    print(f'📊 Fact issues: {fact_issues}')
    
    if issues_count == 0:
        print('❌ No raw data found!')
        sys.exit(1)
    
    if fact_issues == 0 and issues_count > 0:
        print('⚠️ Raw data exists but fact table is empty')
        sys.exit(1)
    
    print('✅ Data verification passed')
    conn.close()
    
except Exception as e:
    print(f'❌ Data verification failed: {e}')
    sys.exit(1)
"
}

# Test dashboard queries
test_dashboard() {
    log_info "Testing dashboard queries..."
    
    python3 -c "
import psycopg2
import pandas as pd
import sys

try:
    conn = psycopg2.connect(
        host='$POSTGRES_HOST',
        port='$POSTGRES_PORT',
        user='$POSTGRES_USER',
        password='$POSTGRES_PASSWORD',
        database='$POSTGRES_DB'
    )
    
    queries = [
        ('Issues Details', '''
            SELECT issue_key, summary, assignee_name, project_name, days_to_resolution
            FROM jira_analytics.fct_issues_details
            LIMIT 1
        '''),
        ('Projects Overview', '''
            SELECT project_name, total_issues, completion_percentage
            FROM jira_analytics.dim_projects
            LIMIT 1
        '''),
        ('Team Performance', '''
            SELECT user_name, status_category, assigned_issues
            FROM jira_analytics.fct_user_performance
            LIMIT 1
        ''')
    ]
    
    for name, query in queries:
        try:
            df = pd.read_sql(query, conn)
            print(f'✅ {name}: {len(df)} rows')
        except Exception as e:
            print(f'❌ {name}: {e}')
            sys.exit(1)
    
    conn.close()
    print('✅ All dashboard queries working')
    
except Exception as e:
    print(f'❌ Dashboard test failed: {e}')
    sys.exit(1)
"
}

# Main execution
main() {
    local action=$1
    shift
    
    case $action in
        "wait-postgres")
            wait_for_postgres
            ;;
        "run-dlt")
            run_dlt "$@"
            ;;
        "run-dbt")
            run_dbt "$@"
            ;;
        "verify-data")
            verify_data
            ;;
        "test-dashboard")
            test_dashboard
            ;;
        *)
            log_error "Unknown action: $action"
            echo "Available: wait-postgres, run-dlt, run-dbt, verify-data, test-dashboard"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
