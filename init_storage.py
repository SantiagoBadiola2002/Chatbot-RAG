import os
import faiss
import pickle
import numpy as np
from datasets import ejemplos
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
)
from llama_index.vector_stores.faiss import FaissVectorStore
from llm_embedding import embed_model

# Directorios
STORAGE_DIR = "./storage"
DOCS_DIR = "./docs"
os.makedirs(STORAGE_DIR, exist_ok=True)

# ==============================
# 🔹 Index de DOCS
# ==============================
docstore_file = os.path.join(STORAGE_DIR, "docstore.json")

if not os.path.exists(docstore_file):
    print("Creando índice de documentos...")

    docs = SimpleDirectoryReader(DOCS_DIR).load_data()
    if len(docs) == 0:
        raise ValueError("No se encontraron documentos en ./docs")

    # Crear FAISS para los documentos
    test_embedding = embed_model.get_text_embedding(docs[0].text)
    EMBED_DIM = len(test_embedding)
    faiss_index = faiss.IndexFlatL2(EMBED_DIM)
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_documents(
        docs,
        embed_model=embed_model,
        storage_context=storage_context
    )

    # Persistir en disco
    index.storage_context.persist(persist_dir=STORAGE_DIR)
    print("Índice de documentos guardado.")
else:
    print("Índice de documentos ya existe. Omitiendo creación.")

# ==============================
# 🔹 Index de ejemplos (router)
# ==============================
faiss_index_path = os.path.join(STORAGE_DIR, "ejemplos_faiss.index")
metadata_path = os.path.join(STORAGE_DIR, "ejemplos_metadata.pkl")

if not os.path.exists(faiss_index_path) or not os.path.exists(metadata_path):
    print("Creando índice FAISS de ejemplos...")

    vectors = [embed_model.get_text_embedding(pregunta) for tipo, pregunta in ejemplos]
    vectors_array = np.array(vectors).astype("float32")
    dim = vectors_array.shape[1]

    faiss_index = faiss.IndexFlatL2(dim)
    faiss_index.add(vectors_array)

    faiss.write_index(faiss_index, faiss_index_path)
    with open(metadata_path, "wb") as f:
        pickle.dump(ejemplos, f)

    print("Índice FAISS y metadatos de ejemplos guardados.")
else:
    print("Índice FAISS de ejemplos ya existe. Omitiendo creación.")
