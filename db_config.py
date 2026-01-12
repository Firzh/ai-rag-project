import chromadb
import os

# Path database sekarang lebih deskriptif
DB_PATH = "./db_personal"

def get_collection(collection_name="general_notes"):
    client = chromadb.PersistentClient(path=DB_PATH)
    return client.get_or_create_collection(name=collection_name)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')