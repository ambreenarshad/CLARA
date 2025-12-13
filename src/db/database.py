"""Database connection and session management."""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from src.utils.config import get_config
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

# Create declarative base
Base = declarative_base()

# Global engine and session maker
_engine = None
_SessionLocal = None


def get_database_url() -> str:
    """
    Get database URL from configuration.

    Returns:
        str: Database connection URL
    """
    config = get_config()
    # Default to SQLite for development
    return getattr(config, 'database_url', 'sqlite:///./nlp_feedback.db')


def init_db():
    """Initialize database engine and session maker."""
    global _engine, _SessionLocal

    if _engine is None:
        database_url = get_database_url()
        logger.info(f"Initializing database: {database_url}")

        # Create engine
        _engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False} if "sqlite" in database_url else {},
            pool_pre_ping=True,
        )

        # Create session maker
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

        logger.info("Database initialized successfully")


def get_engine():
    """
    Get database engine.

    Returns:
        Engine: SQLAlchemy engine
    """
    if _engine is None:
        init_db()
    return _engine


def get_session_local():
    """
    Get session local class.

    Returns:
        sessionmaker: SQLAlchemy session maker
    """
    if _SessionLocal is None:
        init_db()
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for database sessions.

    Yields:
        Session: Database session
    """
    if _SessionLocal is None:
        init_db()

    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    from src.db.models import User, FeedbackBatch, AnalysisResult

    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=get_engine())
    logger.info("Database tables created successfully")
