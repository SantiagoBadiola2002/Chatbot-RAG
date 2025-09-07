# models.py
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI
import os

# 🔑 API Key
os.environ["GOOGLE_API_KEY"] = "TU_GOOGLE_API_KEY"  # reemplaza con la tuya

# Instancia global de embeddings
embed_model = GoogleGenAIEmbedding(model_name="text-embedding-004")

# Instancia global de LLM
llm = GoogleGenAI(model="gemini-2.0-flash")
