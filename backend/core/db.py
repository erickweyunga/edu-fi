from typing import AsyncGenerator
import time
import logging
import asyncio
from contextlib import asynccontextmanager

from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from core.config import settings

logger = logging.getLogger(__name__)

# Create async engine with connection pooling and pre-ping
engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=settings.SQL_ECHO,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    pool_pre_ping=True,  # Check connection before using from pool
)

# Session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# async def init_db(max_retries=5, retry_interval=2):
#     """
#     Initialize database tables with retry logic

#     Args:
#         max_retries: Maximum number of connection attempts
#         retry_interval: Initial seconds to wait between retries (doubles each retry)
#     """
#     for attempt in range(max_retries):
#         try:
#             logger.info("Attempting to initialize database tables...")
#             async with engine.begin() as conn:
#                 await conn.run_sync(SQLModel.metadata.create_all)
#             logger.info("Database tables initialized successfully")
#             return
#         except OperationalError as e:
#             if attempt < max_retries - 1:
#                 wait_time = retry_interval * (2**attempt)  # Exponential backoff
#                 logger.warning(
#                     f"Database connection failed during initialization. "
#                     f"Retrying in {wait_time} seconds... (Attempt {attempt+1}/{max_retries})"
#                 )
#                 logger.debug(f"Error details: {str(e)}")
#                 await asyncio.sleep(wait_time)
#             else:
#                 logger.error(
#                     f"Failed to initialize database after {max_retries} attempts"
#                 )
#                 raise


@asynccontextmanager
async def get_db_context():
    """
    Async context manager for database sessions
    """
    session = async_session()
    try:
        yield session
        await session.commit()
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database session
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            await session.close()


async def check_db_connection(max_retries=5):
    """
    Utility function to check database connectivity

    Returns True if connection is successful, False otherwise
    """
    for attempt in range(max_retries):
        try:
            async with engine.connect() as conn:
                await conn.execute("SELECT 1")
                logger.info("Database connection successful")
                return True
        except OperationalError as e:
            wait_time = 2**attempt
            logger.warning(
                f"Database connection check failed. "
                f"Retrying in {wait_time} seconds... (Attempt {attempt+1}/{max_retries})"
            )
            logger.debug(f"Error details: {str(e)}")
            await asyncio.sleep(wait_time)

    logger.error(f"Database connection check failed after {max_retries} attempts")
    return False
