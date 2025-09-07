import os
import logging
from sqlalchemy import create_engine, inspect
from llama_index.core import StorageContext, load_index_from_storage, SQLDatabase
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llm_embedding import embed_model, llm
from router import detectar_intencion  # Función de intención ya preparada
import numpy as np
import faiss
import pickle

# ==============================
# 🔑 Configuración
# ==============================
logging.basicConfig(level=logging.WARNING)

STORAGE_DIR = "./storage"
persist_dir = STORAGE_DIR
docstore_file = os.path.join(persist_dir, "docstore.json")

# ==============================
# ⚙️ Conexión a MySQL
# ==============================
engine = create_engine("mysql+pymysql://root:@localhost/tracking_db")
sql_database = SQLDatabase(engine)
inspector = inspect(engine)
tablas_db = inspector.get_table_names()

# ==============================
# 🔹 Cargar índice FAISS de documentos
# ==============================
if not os.path.exists(docstore_file):
    raise FileNotFoundError("No se encontró el índice de documentos. Ejecuta init_storage.py primero.")

vector_store = FaissVectorStore.from_persist_dir(persist_dir)
storage_context = StorageContext.from_defaults(
    vector_store=vector_store,
    persist_dir=persist_dir
)
index = load_index_from_storage(storage_context, embed_model=embed_model)
chatbot_docs = index.as_chat_engine(llm=llm)

# ==============================
# 🔹 Configuración SQL
# ==============================
sql_query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables=tablas_db,
    llm=llm,
    embed_model=embed_model
)

# ==============================
# 🔹 Cargar índice FAISS de ejemplos (router)
# ==============================
faiss_index_path = os.path.join(STORAGE_DIR, "ejemplos_faiss.index")
metadata_path = os.path.join(STORAGE_DIR, "ejemplos_metadata.pkl")

if not os.path.exists(faiss_index_path) or not os.path.exists(metadata_path):
    raise FileNotFoundError("No se encontró el índice FAISS de ejemplos. Ejecuta init_storage.py primero.")

faiss_index = faiss.read_index(faiss_index_path)
with open(metadata_path, "rb") as f:
    ejemplos_list = pickle.load(f)

# ==============================
# 🤖 Chat híbrido
# ==============================
def hybrid_chatbot(user_input: str):
    try:
        tipo = detectar_intencion(user_input)  # Usa el índice persistente

        if tipo == "SQL":
            respuesta_sql = sql_query_engine.query(user_input)
            respuesta = f"📊 Datos obtenidos:\n{respuesta_sql}" if respuesta_sql else "❗ No encontré resultados."
        elif tipo == "DOCS":
            respuesta = chatbot_docs.chat(user_input).response
        else:
            respuesta = "❓ No estoy seguro de cómo responder a eso."

        return respuesta

    except Exception as e:
        logging.error(f"Error procesando la pregunta: {user_input} | {e}")
        return "⚠️ Hubo un error procesando tu pregunta."
