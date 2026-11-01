from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

database_url = settings.database_url
if database_url.startswith("postgres://"):
    database_url = "postgresql+psycopg://" + database_url.removeprefix("postgres://")
elif database_url.startswith("postgresql://"):
    database_url = "postgresql+psycopg://" + database_url.removeprefix("postgresql://")
connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
engine = create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_schema():
    """Create tables and add new nullable Gmail metadata columns to existing local DBs."""
    Base.metadata.create_all(bind=engine)
    existing = {column["name"] for column in inspect(engine).get_columns("emails")}
    with engine.begin() as connection:
        if "thread_id" not in existing:
            connection.execute(text("ALTER TABLE emails ADD COLUMN thread_id VARCHAR(200)"))
        if "original_message_id" not in existing:
            connection.execute(text("ALTER TABLE emails ADD COLUMN original_message_id VARCHAR(500)"))
        if "gmail_draft_id" not in existing:
            connection.execute(text("ALTER TABLE emails ADD COLUMN gmail_draft_id VARCHAR(200)"))
