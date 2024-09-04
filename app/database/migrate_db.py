from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL_SYNC
from app.database.models import Base

engine = create_engine(DATABASE_URL_SYNC)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def drop_all_tables(engine):
    meta = MetaData()
    meta.reflect(bind=engine)
    meta.drop_all(bind=engine)


def create_all_tables(engine):
    Base.metadata.create_all(engine)
