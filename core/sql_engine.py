from llama_index.core.query_engine import NLSQLTableQueryEngine
from llm_embedding import llm, embed_model
from core.database import get_sql_database


def init_sql_engine():
    sql_db, tablas = get_sql_database()
    return NLSQLTableQueryEngine(
        sql_database=sql_db, tables=tablas, llm=llm, embed_model=embed_model
    )
