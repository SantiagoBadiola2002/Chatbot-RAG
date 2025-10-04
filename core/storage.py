# core/storage.py
import os
import faiss
import pickle
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core import StorageContext, load_index_from_storage
from llm_embedding import embed_model
from config import STORAGE_DIR, DOCSTORE_FILE, FAISS_INDEX_FILE, METADATA_FILE


def load_doc_index():
    """
    Carga el índice de documentos desde storage/.
    """
    if not os.path.exists(DOCSTORE_FILE):
        raise FileNotFoundError(
            "No se encontró docstore.json. Ejecuta init_storage.py primero."
        )

    vector_store = FaissVectorStore.from_persist_dir(STORAGE_DIR)
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store, persist_dir=STORAGE_DIR
    )
    return load_index_from_storage(storage_context, embed_model=embed_model)


def load_examples_index():
    """
    Carga el índice FAISS de ejemplos y sus metadatos.
    """
    if not os.path.exists(FAISS_INDEX_FILE) or not os.path.exists(METADATA_FILE):
        raise FileNotFoundError(
            "No se encontró el índice FAISS de ejemplos. Ejecuta init_storage.py primero."
        )

    faiss_index = faiss.read_index(FAISS_INDEX_FILE)
    with open(METADATA_FILE, "rb") as f:
        metadata = pickle.load(f)

    return faiss_index, metadata
