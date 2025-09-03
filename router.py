from llama_index.llms.google_genai import GoogleGenAI
from datasets import ejemplos  # tu lista de tuples ("sql"/"docs", "pregunta")
from llama_index.core.prompts import RichPromptTemplate
import os
import logging

os.environ["GOOGLE_API_KEY"] = "TU_API_KEY_AQUI"  # Reemplaza con tu clave real
llm = GoogleGenAI(model="gemini-2.0-flash")

# Configuración logging
logging.basicConfig(level=logging.INFO)

# Template para routing
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

def detectar_intencion(user_input: str, llm) -> str:
    """
    Decide si la pregunta debe ir a SQL o Docs usando LLM y few-shot.
    """
    try:
        # Formatear como lista de mensajes de chat
        messages = routing_template.format_messages(
            user_input=user_input,
            ejemplos=ejemplos[:10]  # few-shot
        )

        # Llamar al LLM en modo chat
        respuesta = llm.chat(messages)

        return respuesta.message.content.strip().upper()

    except Exception as e:
        logging.error(f"Error al predecir intención: {user_input} | {e}")
        return "UNKNOWN"