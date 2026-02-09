from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@event.listens_for(engine, "connect")
def _enable_pgvector(dbapi_connection, connection_record):
    with dbapi_connection.cursor() as cursor:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
    dbapi_connection.commit()

class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
