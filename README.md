# Chatbot-RAG

Un chatbot basado en **RAG (Retrieval-Augmented Generation)** usando `llama-index`, `Google GenAI` y `FAISS` como vector store. Permite responder preguntas sobre documentos cargados en la carpeta `./docs/`.

---

## 🔹 Tecnologías utilizadas

- Python 3.10+
- [llama-index](https://pypi.org/project/llama-index/)
- [Google GenAI](https://cloud.google.com/genai)
- FAISS
- SQLAlchemy y PyMySQL para interacción con MySQL
- Flask para la interfaz gráfica

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

```bash
pip install -r requirements.txt
```

## 3. Configurar credenciales

 ### Agrega tu clave de API de Google en llm_embedding.py:

```bash
export GOOGLE_API_KEY="TU_API_KEY"   # Linux/macOS

set GOOGLE_API_KEY="TU_API_KEY"      # Windows
```

## 4.📂 Preparar documentos

Coloca todos tus archivos .txt o documentos en la carpeta ./docs/. Estos serán indexados por el vector store.

## 5. Configurar base de datos MySQL

1. Asegúrate de tener MySQL corriendo y la base de datos creada:

```sql
CREATE DATABASE tracking_db;
```

2. Crea las tablas

```sql
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 
```

```sql
CREATE TABLE camiones (
    id_camion INT AUTO_INCREMENT PRIMARY KEY,
    placa VARCHAR(20) UNIQUE NOT NULL,
    modelo VARCHAR(50),
    capacidad DECIMAL(10,2), -- en toneladas
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

```sql
CREATE TABLE paquetes (
    id_paquete INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    numero_seguimiento VARCHAR(50) UNIQUE NOT NULL,
    origen VARCHAR(100),
    destino VARCHAR(100),
    estado VARCHAR(50) DEFAULT 'Pendiente',
    id_camion INT, -- Opcional: el camión asignado
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_camion) REFERENCES camiones(id_camion)
);
```

```sql
CREATE TABLE historial_seguimiento (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_paquete INT NOT NULL,
    estado VARCHAR(50) NOT NULL,
    ubicacion VARCHAR(100),
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_paquete) REFERENCES paquetes(id_paquete)
);
```

3. Actualiza la conexión en main.py:

`engine = create_engine("mysql+pymysql://root:@localhost/tracking_db")`


## 7. Crear los embedding de los documentos y de los datasets

`python init_storage.py`

## 8. 🖥️ Uso con interfaz gráfica

1. Ejecutar el chatbot:

    `python gui.py`

2. Abre tu navegador y entra a:

    `http://127.0.0.1:5000`

3. Para salir, usa ctrl+C en consola.

## Sesiones y aislamiento de contexto

El chatbot ahora soporta sesiones separadas por `session_id`. Cada cliente que abra la interfaz web recibirá un `session_id` generado y almacenado en `localStorage`. Ese `session_id` se envía con cada petición al backend y el servidor mantiene un chat engine separado por sesión en memoria.

Notas importantes:
- Esto evita que las conversaciones de distintos usuarios se mezclen.
- Implementación actual: store en memoria (diccionario protegido por lock). Funciona bien en un solo proceso/worker.
- Para despliegues con múltiples procesos o instancias (gunicorn con varios workers, múltiples containers), usa un store compartido (por ejemplo Redis) o un diseño que centralice el estado. De lo contrario las sesiones no se compartirán entre procesos.

Si deseas que implemente soporte con Redis (recomendado para producción), puedo añadir un ejemplo y dependencias.

💡 Notas

El entorno virtual no se sube a GitHub. Usa requirements.txt para instalar dependencias:

```bash
pip freeze > requirements.txt
pip install -r requirements.txt
```