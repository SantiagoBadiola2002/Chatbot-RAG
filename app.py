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
from router import detectar_intencion 

# ==============================
# 🔑 Configuración
# ==============================
logging.basicConfig(level=logging.WARNING)
os.environ["GOOGLE_API_KEY"] = "TU_API_KEY_AQUI"  # Reemplaza con tu clave real

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
    url="TU_QDRANT_URL_AQUI",  # Reemplaza con tu URL real
    api_key="TU_QDRANT_API_KEY_AQUI"  # Reemplaza con tu API Key real
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
    try:
        tipo = detectar_intencion(user_input, llm)

        if tipo == "SQL":
            respuesta_sql = sql_query_engine.query(user_input)
            if not respuesta_sql:
                respuesta = "❗ No encontré resultados para esa consulta."
            else:
                respuesta = f"📊 Datos obtenidos:\n{respuesta_sql}"

        elif tipo == "DOCS":
            # Aquí iría tu motor de documentos Qdrant
             respuesta = chatbot_docs.chat(user_input).response

        else:
            logging.warning(f"Intención no clara: {user_input}")
            respuesta = "❓ No estoy seguro de cómo responder a eso. Lo estoy registrando para mejorar."

        # Logear QA
        #log_qa(user_input, respuesta)
        return respuesta

    except Exception as e:
        logging.error(f"Error al procesar la pregunta: {user_input} | {e}")
        return "⚠️ Hubo un error procesando tu pregunta. Se registró para revisión."


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

