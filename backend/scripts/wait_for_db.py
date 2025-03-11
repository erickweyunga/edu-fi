#!/usr/bin/env python
"""
Script to wait for the database to become available
"""

import asyncio
import os
import sys
import time
import logging
import asyncpg

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("wait-for-db")

# Database connection parameters
DB_HOST = os.environ.get("POSTGRES_SERVER", "db")
DB_PORT = int(os.environ.get("POSTGRES_PORT", "5432"))
DB_USER = os.environ.get("POSTGRES_USER", "postgres")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
DB_NAME = os.environ.get("POSTGRES_DB", "edu_fi")

# Connection timeout settings
MAX_RETRIES = 30
RETRY_INTERVAL = 2


async def check_db_connection():
    """
    Check if the database is accessible.

    Returns True if connection is successful, False otherwise
    """
    try:
        conn = await asyncpg.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            timeout=3,  # 3 seconds connection timeout
        )
        await conn.execute("SELECT 1")
        await conn.close()
        return True
    except Exception as e:
        logger.debug(f"Database connection failed: {str(e)}")
        return False


async def wait_for_db():
    """
    Wait for database to become available
    """
    logger.info(f"Waiting for PostgreSQL at {DB_HOST}:{DB_PORT}...")

    for attempt in range(1, MAX_RETRIES + 1):
        if await check_db_connection():
            logger.info(f"✅ PostgreSQL is available at {DB_HOST}:{DB_PORT}")
            return True

        logger.info(
            f"Attempt {attempt}/{MAX_RETRIES} - Database not available. Retrying in {RETRY_INTERVAL} seconds..."
        )
        await asyncio.sleep(RETRY_INTERVAL)

    logger.error(f"❌ Failed to connect to PostgreSQL after {MAX_RETRIES} attempts")
    return False


if __name__ == "__main__":
    logger.info(
        f"Checking connection to PostgreSQL ({DB_HOST}:{DB_PORT}, database: {DB_NAME})"
    )

    if asyncio.run(wait_for_db()):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure
