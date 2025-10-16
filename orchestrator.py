import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import dlt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class JiraDataPipeline:
    """Complete Jira data ingestion and transformation pipeline"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dbt_project_dir = "/app/dbt"
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)

    def get_dlt_pipeline(self, pipeline_name: str) -> dlt.Pipeline:
        """Creates configured dlt pipeline"""
        return dlt.pipeline(
            pipeline_name=pipeline_name,
            destination="postgres",
            dataset_name="jira_data",
            progress="log",
            dev_mode=False,
        )

    def extract_data(self, data_type: str = "all") -> bool:
        """Executes data extraction using dlt"""
        logger.info(f"Starting data extraction: {data_type}")

        try:
            pipeline = self.get_dlt_pipeline(f"jira_{data_type}")

            if data_type == "all":
                return self._extract_all_data(pipeline)
            elif data_type == "issues":
                return self._extract_issues_only(pipeline)
            elif data_type == "projects":
                return self._extract_projects_only(pipeline)
            elif data_type == "users":
                return self._extract_users_only(pipeline)
            else:
                logger.error(f"Unsupported data type: {data_type}")
                return False

        except Exception as e:
            logger.error(f"Error in data extraction: {e}")
            return False

    def _extract_all_data(self, pipeline: dlt.Pipeline) -> bool:
        """Extracts all Jira data"""
        from jira import jira, jira_search

        try:
            logger.info("Extracting projects...")
            projects_resource = jira().projects
            pipeline.run([projects_resource])
            logger.info("Projects extracted successfully")

            logger.info("Extracting users...")
            users_resource = jira().users
            pipeline.run([users_resource])
            logger.info("Users extracted successfully")

            logger.info("Extracting issues...")
            issues_resource = jira_search().issues(jql_queries=['updated >= "-5d"'])
            pipeline.run([issues_resource])
            logger.info("Issues extracted successfully")

            return True

        except Exception as e:
            logger.error(f"Error in complete extraction: {e}")
            return False

    def _extract_issues_only(self, pipeline: dlt.Pipeline) -> bool:
        """Extracts only issues"""
        from jira import jira_search

        try:
            issues_resource = jira_search().issues(jql_queries=['updated >= "-30d"'])
            pipeline.run([issues_resource])
            logger.info("Issues extracted successfully")
            return True
        except Exception as e:
            logger.error(f"Error in issues extraction: {e}")
            return False

    def _extract_projects_only(self, pipeline: dlt.Pipeline) -> bool:
        """Extracts only projects"""
        from jira import jira

        try:
            projects_resource = jira().projects
            pipeline.run([projects_resource])
            logger.info("Projects extracted successfully")
            return True
        except Exception as e:
            logger.error(f"Error in projects extraction: {e}")
            return False

    def _extract_users_only(self, pipeline: dlt.Pipeline) -> bool:
        """Extracts only users"""
        from jira import jira

        try:
            users_resource = jira().users
            pipeline.run([users_resource])
            logger.info("Users extracted successfully")
            return True
        except Exception as e:
            logger.error(f"Error in users extraction: {e}")
            return False

    def transform_data(self, dbt_command: str = "run") -> bool:
        """Executes transformations using dbt"""
        logger.info(f"Starting data transformation: dbt {dbt_command}")

        try:
            if os.path.exists("/app/dbt"):
                dbt_dir = Path("/app/dbt")
            else:
                dbt_dir = Path("/home/alfprado/dev/Flexiana/dlt_jira/dbt")

            if not dbt_dir.exists():
                logger.error(f"dbt directory not found: {dbt_dir.absolute()}")
                return False

            env = os.environ.copy()
            env["DBT_LOG_PATH"] = "/tmp/dbt_logs"

            original_cwd = os.getcwd()
            os.chdir(dbt_dir)

            try:
                cmd = f"dbt {dbt_command} --log-level info"
                logger.info(f"Executing: {cmd} in {dbt_dir}")

                result_code = os.system(cmd)

                if result_code == 0:
                    logger.info(f"dbt {dbt_command} executed successfully")
                    return True
                else:
                    logger.error(f"dbt {dbt_command} failed with code {result_code}")
                    return False

            finally:
                os.chdir(original_cwd)

        except subprocess.TimeoutExpired:
            logger.error("dbt timeout - process took more than 30 minutes")
            return False
        except Exception as e:
            logger.error(f"Error executing dbt: {e}")
            return False

    def run_full_pipeline(
        self, data_type: str = "all", dbt_command: str = "run"
    ) -> bool:
        """Executes complete pipeline: extraction + transformation"""
        logger.info("Starting complete Jira data pipeline")
        logger.info("=" * 60)

        start_time = datetime.now()

        logger.info("STEP 1: DATA EXTRACTION")
        logger.info("-" * 40)
        if not self.extract_data(data_type):
            logger.error("Data extraction failed. Aborting pipeline.")
            return False

        logger.info("\nSTEP 2: DATA TRANSFORMATION")
        logger.info("-" * 40)
        if not self.transform_data(dbt_command):
            logger.error("Data transformation failed.")
            return False

        end_time = datetime.now()
        duration = end_time - start_time

        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info(f"Total duration: {duration}")
        logger.info(f"Extracted data: {data_type}")
        logger.info(f"Transformation: dbt {dbt_command}")
        logger.info("=" * 60)

        return True

    def run_dbt_only(self, dbt_command: str = "run") -> bool:
        """Executes only dbt transformations (without extraction)"""
        logger.info(f"Executing only dbt {dbt_command}")
        return self.transform_data(dbt_command)

    def run_extraction_only(self, data_type: str = "all") -> bool:
        """Executes only data extraction (without transformation)"""
        logger.info(f"Executing only extraction: {data_type}")
        return self.extract_data(data_type)


def main():
    """Main function for command line execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Jira data pipeline with dbt")
    parser.add_argument(
        "--mode",
        choices=["full", "extract", "transform"],
        default="full",
        help="Execution mode",
    )
    parser.add_argument(
        "--data-type",
        choices=["all", "issues", "projects", "users"],
        default="all",
        help="Data type to extract",
    )
    parser.add_argument(
        "--dbt-command",
        default="run",
        help="dbt command to execute (run, test, docs, etc.)",
    )

    args = parser.parse_args()

    # Pipeline configuration
    config = {
        "pipeline_name": "jira_analytics",
        "destination": "postgres",
        "dataset_name": "jira_data",
    }

    # Create and execute pipeline
    pipeline = JiraDataPipeline(config)

    try:
        if args.mode == "full":
            success = pipeline.run_full_pipeline(args.data_type, args.dbt_command)
        elif args.mode == "extract":
            success = pipeline.run_extraction_only(args.data_type)
        elif args.mode == "transform":
            success = pipeline.run_dbt_only(args.dbt_command)

        if success:
            logger.info("Pipeline executed successfully!")
            sys.exit(0)
        else:
            logger.error("Pipeline failed!")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
