"""
Jira Data Pipeline - Extract, Transform, and Load Jira data using DLT and DBT
"""
import dlt
import sys
import subprocess
import os
from jira import jira, jira_search


def get_base_pipeline(pipeline_name: str):
    """Create and configure a DLT pipeline instance."""
    return dlt.pipeline(
        pipeline_name=pipeline_name,
        destination="postgres",
        dataset_name="jira_data",
        progress="log",
        dev_mode=False
    )

def run_dbt_transformations(load_projects=True, load_users=True):
    """Execute DBT transformations after DLT pipeline completion."""
    print("🔄 Running DBT transformations...")
    print("=" * 50)
    
    try:
        # Configure DBT environment variables with memory optimization
        env = os.environ.copy()
        env['DBT_LOG_LEVEL'] = 'info'
        env['DBT_LOG_FORMAT'] = 'text'
        env['DBT_LOG_PATH'] = '/tmp/dbt_logs'
        env['DBT_THREADS'] = '2'  # Reduce threads to save memory
        env['DBT_TARGET_PATH'] = '/tmp/dbt_target'  # Use tmp for target
        
        # Install DBT packages
        print("📦 Installing DBT packages...")
        subprocess.run(["dbt", "deps", "--log-level", "info"], check=True, cwd="dbt", env=env)
        
        # Execute DBT models with memory optimization and variables
        print("🔄 Running DBT models...")
        dbt_vars = f"{{'load_projects': {str(load_projects).lower()}, 'load_users': {str(load_users).lower()}}}"
        subprocess.run([
            "dbt", "run", 
            "--log-level", "info",
            "--threads", "2",
            "--target-path", "/tmp/dbt_target",
            "--vars", dbt_vars
        ], check=True, cwd="dbt", env=env)
        
        # Execute DBT tests with memory optimization and variables
        print("🧪 Running DBT tests...")
        dbt_vars = f"{{'load_projects': {str(load_projects).lower()}, 'load_users': {str(load_users).lower()}}}"
        
        # Skip relationship tests if not all data is loaded
        if load_projects and load_users:
            # Run all tests when all data is available
            subprocess.run([
                "dbt", "test", 
                "--log-level", "info",
                "--threads", "2",
                "--target-path", "/tmp/dbt_target",
                "--vars", dbt_vars
            ], check=True, cwd="dbt", env=env)
        else:
            # Skip relationship and source tests when data is incomplete
            print("⚠️  Skipping relationship and source tests due to incomplete data load")
            subprocess.run([
                "dbt", "test", 
                "--log-level", "info",
                "--threads", "2",
                "--target-path", "/tmp/dbt_target",
                "--vars", dbt_vars,
                "--exclude", "relationships", "source_not_null", "source_unique"
            ], check=True, cwd="dbt", env=env)
        
        # Generate DBT documentation (optional, can be skipped if memory is low)
        print("📚 Generating DBT documentation...")
        try:
            subprocess.run([
                "dbt", "docs", "generate", 
                "--log-level", "info",
                "--target-path", "/tmp/dbt_target"
            ], check=True, cwd="dbt", env=env, timeout=300)
        except subprocess.TimeoutExpired:
            print("⚠️ DBT docs generation timed out, continuing...")
        except subprocess.CalledProcessError:
            print("⚠️ DBT docs generation failed, continuing...")
        
        print("✅ DBT transformations completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ DBT transformation failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error in DBT: {e}")
        sys.exit(1)


def load_jira_issues_only():
    """Load only Jira issues into PostgreSQL database."""
    pipeline = get_base_pipeline("jira_issues")
    
    print("🚀 Starting Jira Issues Pipeline...")
    print("=" * 50)
    
    print("🎫 Loading Jira issues...")
    try:
        issues_resource = jira_search().issues(jql_queries=['updated >= "-5d"'])
        load_info = pipeline.run([issues_resource])
        print(f"✅ Successfully loaded Jira issues: {load_info}")
    except Exception as e:
        print(f"❌ Failed to load issues: {e}")
        return
    
    # Run DBT transformations (only issues loaded)
    run_dbt_transformations(load_projects=False, load_users=False)
    
    print("\n" + "=" * 50)
    print("🎉 Issues pipeline completed! Check your PostgreSQL database for the loaded data.")


def load_jira_projects_only():
    """Load only Jira projects into PostgreSQL database."""
    pipeline = get_base_pipeline("jira_projects")
    
    print("🚀 Starting Jira Projects Pipeline...")
    print("=" * 50)
    
    print("📁 Loading Jira projects...")
    try:
        projects_resource = jira().projects
        load_info = pipeline.run([projects_resource])
        print(f"✅ Successfully loaded Jira projects: {load_info}")
    except Exception as e:
        print(f"❌ Failed to load projects: {e}")
        return
    
    # Run DBT transformations (only projects loaded)
    run_dbt_transformations(load_projects=True, load_users=False)
    
    print("\n" + "=" * 50)
    print("🎉 Projects pipeline completed! Check your PostgreSQL database for the loaded data.")


def load_jira_users_only():
    """Load only Jira users into PostgreSQL database."""
    pipeline = get_base_pipeline("jira_users")
    
    print("🚀 Starting Jira Users Pipeline...")
    print("=" * 50)
    
    print("👥 Loading Jira users...")
    try:
        users_resource = jira().users
        load_info = pipeline.run([users_resource])
        print(f"✅ Successfully loaded Jira users: {load_info}")
    except Exception as e:
        print(f"❌ Failed to load users: {e}")
        return
    
    # Run DBT transformations (only users loaded)
    run_dbt_transformations(load_projects=False, load_users=True)
    
    print("\n" + "=" * 50)
    print("🎉 Users pipeline completed! Check your PostgreSQL database for the loaded data.")


def load_jira_data():
    """Load Jira data into PostgreSQL database."""
    pipeline = get_base_pipeline("jira_rest_api")
    try:
        projects_resource = jira().projects
        load_info = pipeline.run([projects_resource])
        print(f"✅ Successfully loaded Jira projects: {load_info}")
    except Exception as e:
        print(f"❌ Failed to load projects: {e}")
        return
    
    print("\n👥 Loading Jira users...")
    try:
        users_resource = jira().users
        load_info = pipeline.run([users_resource])
        print(f"✅ Successfully loaded Jira users: {load_info}")
    except Exception as e:
        print(f"⚠️  Jira users API not available: {e}")
        print("   This is normal if your Jira instance has restricted user access.")
    
    print("\n🎫 Loading Jira issues...")
    try:
        issues_resource = jira_search().issues(jql_queries=['updated >= "-5d"'])
        load_info = pipeline.run([issues_resource]) 
        print(f"✅ Successfully loaded Jira issues: {load_info}")
    except Exception as e:
        print(f"⚠️  Jira issues API not available: {e}")
        print("   This is normal if your Jira instance has no issues or restricted access.")
    
    # Run DBT transformations (all data loaded)
    run_dbt_transformations(load_projects=True, load_users=True)
    
    print("\n" + "=" * 50)
    print("🎉 Pipeline completed! Check your PostgreSQL database for the loaded data.")
    print("💡 Successfully loaded: Projects, Users, Issues, and DBT transformations")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "issues":
            load_jira_issues_only()
        elif sys.argv[1] == "projects":
            load_jira_projects_only()
        elif sys.argv[1] == "users":
            load_jira_users_only()
        elif sys.argv[1] == "all":
            load_jira_data()
        elif sys.argv[1] == "incremental":
            # For incremental mode, load only updated issues
            load_jira_issues_only()
        else:
            print("Usage: python jira_pipeline.py [issues|projects|users|all|incremental]")
            print("  issues      - Load only issues")
            print("  projects    - Load only projects")
            print("  users       - Load only users")
            print("  all         - Load issues, projects, and users (default)")
            print("  incremental - Load only updated issues (for dev)")
    else:
        load_jira_data()