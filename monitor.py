#!/usr/bin/env python3
"""
Pipeline data monitoring script
"""

import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psycopg2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PipelineMonitor:
    """Monitors the data pipeline status"""

    def __init__(self, db_config):
        self.db_config = db_config

    def check_data_freshness(self):
        """Checks data freshness"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT MAX(fields__updated) as last_update
                FROM jira_data.issues
            """
            )

            result = cursor.fetchone()
            if result and result[0]:
                last_update = result[0]

                # Handle timezone-aware datetime comparison
                if last_update.tzinfo is None:
                    last_update = last_update.replace(tzinfo=timezone.utc)

                now = datetime.now(timezone.utc)
                hours_ago = (now - last_update).total_seconds() / 3600

                logger.info(f"Last issues update: {last_update}")
                logger.info(f"Data is {hours_ago:.1f} hours old")

                if hours_ago > 24:
                    logger.warning("Data is outdated (more than 24h)")
                else:
                    logger.info("Data is up to date")

            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"Error checking data: {e}")

    def check_dbt_models(self):
        """Checks if dbt models were executed"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'jira_analytics'
                AND (table_name LIKE 'dim_%' OR table_name LIKE 'fct_%')
            """
            )

            tables = cursor.fetchall()
            logger.info(f"dbt models found: {len(tables)}")

            for table in tables:
                logger.info(f"  - {table[0]}")

            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"Error checking dbt models: {e}")

    def check_data_quality(self):
        """Checks data quality"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM jira_data.issues")
            issues_count = cursor.fetchone()[0]
            logger.info(f"Total issues: {issues_count}")

            cursor.execute("SELECT COUNT(*) FROM jira_data.projects")
            projects_count = cursor.fetchone()[0]
            logger.info(f"Total projects: {projects_count}")

            cursor.execute("SELECT COUNT(*) FROM jira_data.users")
            users_count = cursor.fetchone()[0]
            logger.info(f"Total users: {users_count}")

            cursor.execute(
                """
                SELECT COUNT(*) 
                FROM jira_data.issues 
                WHERE fields__summary IS NULL
            """
            )
            null_summaries = cursor.fetchone()[0]
            if null_summaries > 0:
                logger.warning(f"{null_summaries} issues without summary")

            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"Error checking data quality: {e}")


def main():
    """Main monitoring function"""

    db_config = {
        "host": "localhost",
        "port": 5432,
        "database": "jira_dw",
        "user": "dlt_user",
        "password": "dlt_password",
    }

    monitor = PipelineMonitor(db_config)

    logger.info("Starting pipeline monitoring...")
    logger.info("=" * 50)

    monitor.check_data_freshness()
    print()
    monitor.check_dbt_models()
    print()
    monitor.check_data_quality()

    logger.info("=" * 50)
    logger.info("Monitoring completed")


if __name__ == "__main__":
    main()
