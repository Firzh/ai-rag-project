import chromadb
import os

DB_PATH = "./db_personal"

def get_client():
    return chromadb.PersistentClient(path=DB_PATH)

def get_collection(collection_name="general"):
    client = get_client()
    return client.get_or_create_collection(name=collection_name)

def list_all_collections():
    client = get_client()
    # Mengambil semua objek koleksi dan mengembalikan daftar namanya
    return [c.name for c in client.list_collections()]

def clear_screen():
    # 1. Gunakan perintah sistem standar
    os.system('cls' if os.name == 'nt' else 'clear')
    # 2. Tambahkan ANSI Escape Code untuk memaksa kursor ke pojok kiri atas (H) 
    # dan menghapus seluruh layar serta buffer (2J)
    print("\033[H\033[2J", end="", flush=True)