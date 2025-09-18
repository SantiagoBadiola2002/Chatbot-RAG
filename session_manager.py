import threading
from typing import Optional


class SessionManager:
    """Maneja chat engines por session_id en memoria.

    Para crear engines usa el objeto `index` que debe implementar
    `as_chat_engine(llm=...)`.
    """

    def __init__(self, index, llm=None):
        self._lock = threading.Lock()
        self._sessions = {}
        self._index = index
        self._llm = llm
        # Engine compartido por defecto
        try:
            self._global_engine = self._index.as_chat_engine(llm=self._llm)
        except Exception:
            # En caso de que el index no esté listo (tests), deferiremos la creación
            self._global_engine = None

    def get_engine(self, session_id: Optional[str]):
        if not session_id:
            if self._global_engine is None:
                self._global_engine = self._index.as_chat_engine(llm=self._llm)
            return self._global_engine

        with self._lock:
            engine = self._sessions.get(session_id)
            if engine is None:
                engine = self._index.as_chat_engine(llm=self._llm)
                self._sessions[session_id] = engine
            return engine

    def clear_session(self, session_id: str):
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
