import logging
from router import detectar_intencion
from core.sql_engine import init_sql_engine
from core.doc_engine import init_doc_engine

sql_engine = init_sql_engine()
session_manager = init_doc_engine()


def hybrid_chatbot(user_input: str, session_id: str = None):
    try:
        tipo = detectar_intencion(user_input)

        if tipo == "SQL":
            result = sql_engine.query(user_input)
            return (
                f"📊 Datos obtenidos:\n{result}"
                if result
                else "❗ No encontré resultados."
            )

        elif tipo == "DOCS":
            engine = session_manager.get_engine(session_id)
            return engine.chat(user_input).response

        return "❓ No estoy seguro de cómo responder a eso."
    except Exception as e:
        logging.error(f"Error procesando '{user_input}': {e}")
        return "⚠️ Hubo un error procesando tu pregunta."
