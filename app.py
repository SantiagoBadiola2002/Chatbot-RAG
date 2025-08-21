from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

import os

import logging

# Desactiva logs de nivel INFO y DEBUG (solo muestra WARNING o superior)
logging.basicConfig(level=logging.WARNING)

# ==============================
# 🔑 Configuración de credenciales
# ==============================
os.environ["GOOGLE_API_KEY"] = "TU_GOOGLE_API_KEY"

# Qdrant (Cloud)
qdrant_client = QdrantClient(
    url="TU_QDRANT_URL", 
    api_key="TU_QDRANT_API_KEY",
)

# Codigo para borrar toda la base de datos en Qdrant
#qdrant_client.delete_collection(collection_name="docs_collection")

# ==============================
# ⚙️ Modelos
# ==============================
llm = GoogleGenAI(
    model="gemini-2.0-flash",
)

embed_model = GoogleGenAIEmbedding(
    model_name="text-embedding-004", 
    embed_batch_size=100
)

# ==============================
# 📂 Cargar documentos
# ==============================
docs = SimpleDirectoryReader(input_dir="./docs/").load_data()

# ==============================
# 🗄️ Crear índice en Qdrant
# ==============================
vector_store = QdrantVectorStore(
    client=qdrant_client, 
    collection_name="docs_collection"  # el nombre de tu colección en Qdrant
)

storage_context = StorageContext.from_defaults(vector_store=vector_store)

index = VectorStoreIndex.from_documents(
    docs, 
    embed_model=embed_model,
    storage_context=storage_context
)

# ==============================
# 🤖 Chatbot
# ==============================
chatbot = index.as_chat_engine(llm=llm)

# CHAT
while True:
    print("\n")
    user_input = input("Pregunta: ")
    if user_input.lower() in ["exit", "salir"]:
        print("Hasta luego!")
        break
    response = chatbot.chat(user_input)
    print(f"\nRespuesta IA: {response}\n")