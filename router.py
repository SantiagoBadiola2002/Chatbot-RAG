import os
import faiss
import pickle
import numpy as np
from llama_index.core.prompts import RichPromptTemplate
from llm_embedding import embed_model, llm

# ==============================
# 🔹 Rutas de los archivos de storage
# ==============================
STORAGE_DIR = "./storage"
FAISS_INDEX_PATH = os.path.join(STORAGE_DIR, "ejemplos_faiss.index")
METADATA_PATH = os.path.join(STORAGE_DIR, "ejemplos_metadata.pkl")

# ⚠️ Comprobar existencia
if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(METADATA_PATH):
    raise FileNotFoundError(
        f"No se encontraron los archivos de FAISS o metadatos en '{STORAGE_DIR}'. "
        "Ejecuta primero init_storage.py para crearlos."
    )

# ==============================
# 🔹 Cargar índice FAISS y metadatos
# ==============================
faiss_index = faiss.read_index(FAISS_INDEX_PATH)
with open(METADATA_PATH, "rb") as f:
    ejemplos_list = pickle.load(f)

# ==============================
# 🔹 Template de routing
# ==============================
routing_template = RichPromptTemplate(
"""
Decide si la siguiente pregunta debe ir a SQL o Docs.
Responde solo con 'SQL' o 'DOCS'.

{% for tipo, pregunta in ejemplos %}
Pregunta: {{ pregunta }}
Respuesta: {{ tipo }}
{% endfor %}

Pregunta: {{ user_input }}
Respuesta:
"""
)

# ==============================
# 🔹 Función para recuperar ejemplos más similares
# ==============================
def retrieve_similar_examples(user_input, k=6):
    vector = np.array([embed_model.get_text_embedding(user_input)]).astype("float32")
    distances, indices = faiss_index.search(vector, k)
    similares = [ejemplos_list[i] for i in indices[0]]
    return similares

# ==============================
# 🔹 Función para detectar intención (SQL o DOCS)
# ==============================
def detectar_intencion(user_input, k=6):
    ejemplos_cercanos = retrieve_similar_examples(user_input, k)
    messages = routing_template.format_messages(
        user_input=user_input,
        ejemplos=ejemplos_cercanos
    )
    respuesta = llm.chat(messages)
    return respuesta.message.content.strip().upper()
