import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from .config import DATABASE_URL




def create_engine_with_retry():
    max_retries = 10
    delay = 2  

    for attempt in range(1, max_retries + 1):
        try:
            engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,
            )

            with engine.connect() as conn:
                pass

            print("[db] connected to database")
            return engine

        except OperationalError as e:
            print(
                f"[db] database not ready "
                f"(attempt {attempt}/{max_retries}), retrying in {delay}s"
            )
            time.sleep(delay)

    raise RuntimeError("Database not available after retries")


engine = create_engine_with_retry()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass
