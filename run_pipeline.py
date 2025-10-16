#!/usr/bin/env python3
"""
Simplified script to execute the Jira data pipeline
"""

import sys

from orchestrator import JiraDataPipeline


def main():
    """Executes the pipeline with default configurations"""

    config = {
        "pipeline_name": "jira_analytics",
        "destination": "postgres",
        "dataset_name": "jira_data",
    }

    pipeline = JiraDataPipeline(config)
    success = False  # Initialize success variable

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "extract":
            print("Executing data extraction only...")
            success = pipeline.run_extraction_only("all")
        elif command == "transform":
            print("Executing dbt transformation only...")
            success = pipeline.run_dbt_only("run")
        elif command == "test":
            print("Executing dbt tests...")
            success = pipeline.run_dbt_only("test")
        elif command == "docs":
            print("Generating dbt documentation...")
            success = pipeline.run_dbt_only("docs generate")
        else:
            print(f"Unrecognized command: {command}")
            print("Available commands: extract, transform, test, docs")
            sys.exit(1)
    else:
        print("Executing complete pipeline...")
        success = pipeline.run_full_pipeline("all", "run")

    if success:
        print("Pipeline executed successfully!")
        sys.exit(0)
    else:
        print("Pipeline failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
