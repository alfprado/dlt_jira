import dlt
from jira import jira, jira_search

def get_base_pipeline(pipeline_name: str):
    return dlt.pipeline(
        pipeline_name=pipeline_name,
        destination="postgres",
        dataset_name="jira_data",
        progress="log",
        dev_mode=False
    )


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
    
    print("\n" + "=" * 50)
    print("🎉 Pipeline completed! Check your PostgreSQL database for the loaded data.")
    print("💡 Successfully loaded: Projects, Users, and Issues")


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
        else:
            print("Usage: python jira_pipeline.py [issues|projects|users|all]")
            print("  issues   - Load only issues")
            print("  projects - Load only projects")
            print("  users    - Load only users")
            print("  all      - Load issues, projects, and users (default)")
    else:
        load_jira_data()