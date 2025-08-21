# Chatbot-RAG

Un chatbot basado en **RAG (Retrieval-Augmented Generation)** usando `llama-index`, `Google GenAI` y `Qdrant` como vector store. Permite responder preguntas sobre documentos cargados en la carpeta `./docs/`.

---

## 🔹 Tecnologías utilizadas

- Python 3.10+
- [llama-index](https://pypi.org/project/llama-index/)
- [Google GenAI](https://cloud.google.com/genai)
- [Qdrant](https://qdrant.tech/)
- `qdrant-client` para interactuar con la base de datos de vectores

---

## ⚙️ Instalación y configuración

### 1. Crear entorno virtual

```bash
python -m venv env

```
Activar el entorno virtual:

Windows:
    `.\env\Scripts\activate`

Linux:
    `source env/bin/activate`

--

## 2. Instalar dependencias

pip install llama-index llama-index-llms-gemini llama-index-embeddings-gemini

pip install llama-index-llms-google-genai llama-index

pip install llama-index-embeddings-google-genai

pip install qdrant-client

pip install llama-index-vector-stores-qdrant


## 3. Configurar credenciales

 ### Agrega tu clave de API de Google:

```bash
export GOOGLE_API_KEY="TU_API_KEY"   # Linux/macOS

set GOOGLE_API_KEY="TU_API_KEY"      # Windows
```
### Configura Qdrant (Cloud) en el código:
```bash
qdrant_client = QdrantClient(
    url="TU_QDRANT_URL",
    api_key="TU_QDRANT_API_KEY",
)

```

## 4.📂 Preparar documentos

Coloca todos tus archivos .txt o documentos en la carpeta ./docs/. Estos serán indexados por el vector store.

## 5.📝 Uso

1. Ejecutar el chatbot:

    `python main.py`

2. Hacer preguntas al chatbot:

    `Pregunta: ¿Cuál es la función principal del proyecto?`

    `Respuesta IA: ...`

3. Para salir, escribir:

    `exit o salir`


💡 Notas

El entorno virtual no se sube a GitHub. Usa requirements.txt para instalar dependencias:

```bash
pip freeze > requirements.txt
pip install -r requirements.txt
```

Para borrar la base de datos de Qdrant agrega el siguiente codigo:

```bash
qdrant_client.delete_collection(collection_name="docs_collection")
```