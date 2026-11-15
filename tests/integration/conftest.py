# tests/integration/conftest.py
"""Database fixtures for integration tests (PostgreSQL in CI, via DATABASE_URL)."""

import pytest
from sqlalchemy import event
from sqlalchemy.orm import Session

from app import models  # noqa: F401  (registers all tables on Base.metadata)
from app.database import Base, engine as app_engine


@pytest.fixture(scope="session")
def db_engine():
    if app_engine.dialect.name == "sqlite":  # make SQLite enforce foreign keys too
        @event.listens_for(app_engine, "connect")
        def _fk_on(dbapi_conn, _):
            dbapi_conn.execute("PRAGMA foreign_keys=ON")

    Base.metadata.drop_all(app_engine)
    Base.metadata.create_all(app_engine)
    yield app_engine
    Base.metadata.drop_all(app_engine)


@pytest.fixture
def db_session(db_engine):
    """A session whose work is rolled back after each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    yield session
    session.close()
    transaction.rollback()
    connection.close()
