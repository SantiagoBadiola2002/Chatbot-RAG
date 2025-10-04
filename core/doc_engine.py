# core/doc_engine.py

from llm_embedding import llm
from session_manager import SessionManager
from core.storage import load_doc_index


def init_doc_engine():
    """
    Inicializa el SessionManager con el índice de documentos cargado.
    """
    index = load_doc_index()
    return SessionManager(index, llm=llm)
