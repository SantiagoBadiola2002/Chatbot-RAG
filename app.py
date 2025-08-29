from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine
import os
import logging
from sqlalchemy import create_engine, inspect

# ==============================
# 🔑 Configuración
# ==============================
logging.basicConfig(level=logging.WARNING)
os.environ["GOOGLE_API_KEY"] = "TU_GOOGLE_API_KEY"

# ==============================
# ⚙️ Conexión a MySQL
# ==============================
engine = create_engine("mysql+pymysql://root:@localhost/tracking_db")
sql_database = SQLDatabase(engine)

# Obtener automáticamente todas las tablas de la DB
inspector = inspect(engine)
tablas_db = inspector.get_table_names()  # ✅ devuelve lista de strings directamente


# ==============================
# Modelo LLM
# ==============================
llm = GoogleGenAI(model="gemini-2.0-flash")

# ==============================
# ⚙️ Configuración Qdrant
# ==============================
qdrant_client = QdrantClient(
    url="TU_QDRANT_URL",
    api_key="TU_QDRANT_API_KEY"
)

embed_model = GoogleGenAIEmbedding(
    model_name="text-embedding-004",
    embed_batch_size=100
)

vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name="docs_collection"
)

storage_context = StorageContext.from_defaults(vector_store=vector_store)

# ==============================
# 📂 Cargar documentos a Qdrant
# ==============================
docs = SimpleDirectoryReader(input_dir="./docs/").load_data()
index = VectorStoreIndex.from_documents(
    docs,
    embed_model=embed_model,
    storage_context=storage_context
)
chatbot_docs = index.as_chat_engine(llm=llm)

# ==============================
# ⚙️ Configuración SQL
# ==============================
sql_query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables=tablas_db,
    llm=llm,
    embed_model=embed_model 
)


# ==============================
# 🤖 Chat híbrido
# ==============================
def hybrid_chatbot(user_input: str):
    """
    Decide si la pregunta es sobre SQL o documentos y responde.
    - Si menciona tablas, columnas o palabras relacionadas con datos: SQL
    - Sino: documentos (Qdrant)
    """
    user_input_lower = user_input.lower()
    
    # Lista de palabras que sugieren consulta SQL
    sql_keywords = ["paquete", "tracking", "envío", "orden", "camion", "usuario", "historial", "mostrar", "listar", "ver"]
    
    # Detectar si alguna palabra clave aparece o si menciona tablas existentes
    if any(word in user_input_lower for word in sql_keywords) or any(tabla.lower() in user_input_lower for tabla in tablas_db):
        try:
            respuesta_sql = sql_query_engine.query(user_input)
            # Formatear la respuesta en texto amigable
            return f"📊 Datos obtenidos:\n{respuesta_sql}"
        except Exception as e:
            return f"⚠️ Error al consultar la base de datos: {str(e)}"
    else:
        # Pregunta sobre documentos
        return chatbot_docs.chat(user_input)

# ==============================
# 🚀 Bucle de conversación
# ==============================
# if __name__ == "__main__":
#     print("🤖 Chatbot iniciado. Escribe 'exit' o 'salir' para terminar.")
#     while True:
#         user_input = input("\nPregunta: ")
#         if user_input.lower() in ["exit", "salir"]:
#             print("Hasta luego! 👋")
#             break
#         
#         respuesta = hybrid_chatbot(user_input)
#         print(f"\nRespuesta IA: {respuesta}\n")

