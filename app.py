import os
import logging
from sqlalchemy import create_engine, inspect
import faiss
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    SQLDatabase
)
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core.query_engine import NLSQLTableQueryEngine
from router import detectar_intencion  # tu función de intención

# ==============================
# 🔑 Configuración
# ==============================
logging.basicConfig(level=logging.WARNING)
os.environ["GOOGLE_API_KEY"] = "TU_GOOGLE_API_KEY" # Reemplaza con tu API Key

# ==============================
# ⚙️ Conexión a MySQL
# ==============================
engine = create_engine("mysql+pymysql://root:@localhost/tracking_db")
sql_database = SQLDatabase(engine)
inspector = inspect(engine)
tablas_db = inspector.get_table_names()

# ==============================
# Modelo LLM
# ==============================
llm = GoogleGenAI(model="gemini-2.0-flash")

# ==============================
# 🔹 Embeddings
# ==============================
embed_model = GoogleGenAIEmbedding(
    model_name="text-embedding-004",
    embed_batch_size=100
)

persist_dir = "./storage"
os.makedirs(persist_dir, exist_ok=True)
docstore_file = os.path.join(persist_dir, "docstore.json")

# ==============================
# 🔹 Inicialización del índice FAISS en disco
# ==============================
if os.path.exists(docstore_file):
    # Cargar índice FAISS ya persistido
    vector_store = FaissVectorStore.from_persist_dir(persist_dir)
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        persist_dir=persist_dir
    )
    index = load_index_from_storage(storage_context, embed_model=embed_model)

else:
    # Primera vez: crear índice desde documentos
    docs = SimpleDirectoryReader("./docs").load_data()
    if len(docs) == 0:
        raise ValueError("No se encontraron documentos en ./docs")

    # Dimensión del embedding
    test_embedding = embed_model.get_text_embedding(docs[0].text)
    EMBED_DIM = len(test_embedding)

    # ⚡ Crear índice FAISS escalable en disco
    nlist = 100  # Número de clusters (ajusta según tu dataset)
    quantizer = faiss.IndexFlatL2(EMBED_DIM)  # Índice plano usado como cuantizador
    faiss_index = faiss.IndexIVFFlat(quantizer, EMBED_DIM, nlist, faiss.METRIC_L2)

    # Entrenar el índice (requiere algunos vectores de entrenamiento)
    embeddings_to_train = [embed_model.get_text_embedding(doc.text) for doc in docs[:min(1000, len(docs))]]
    embeddings_array = faiss.numpy.array(embeddings_to_train).astype("float32")
    faiss_index.train(embeddings_array)  # Entrena FAISS para clustering

    vector_store = FaissVectorStore(faiss_index=faiss_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Crear índice de documentos
    index = VectorStoreIndex.from_documents(
        docs,
        embed_model=embed_model,
        storage_context=storage_context
    )
    # Persistir índice en disco
    index.storage_context.persist(persist_dir=persist_dir)

# Motor de chat sobre documentos
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
            respuesta = chatbot_docs.chat(user_input).response

        else:
            logging.warning(f"Intención no clara: {user_input}")
            respuesta = "❓ No estoy seguro de cómo responder a eso. Lo estoy registrando para mejorar."

        return respuesta

    except Exception as e:
        logging.error(f"Error al procesar la pregunta: {user_input} | {e}")
        return "⚠️ Hubo un error procesando tu pregunta. Se registró para revisión."
