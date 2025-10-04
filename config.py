# config.py
import os
import logging

STORAGE_DIR = "./storage"
DOCSTORE_FILE = os.path.join(STORAGE_DIR, "docstore.json")
FAISS_INDEX_FILE = os.path.join(STORAGE_DIR, "ejemplos_faiss.index")
METADATA_FILE = os.path.join(STORAGE_DIR, "ejemplos_metadata.pkl")

MYSQL_URI = "mysql+pymysql://root:@localhost/tracking_db"

logging.basicConfig(level=logging.INFO)
