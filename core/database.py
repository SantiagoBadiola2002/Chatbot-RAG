from sqlalchemy import create_engine, inspect
from llama_index.core import SQLDatabase
from config import MYSQL_URI


def get_sql_database():
    engine = create_engine(MYSQL_URI)
    inspector = inspect(engine)
    tablas = inspector.get_table_names()
    return SQLDatabase(engine), tablas
