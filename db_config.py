from chromadb.utils import embedding_functions
import chromadb
import os

DB_PATH = "./db_personal"

def get_client():
    return chromadb.PersistentClient(path=DB_PATH)

def get_collection(collection_name):
    # Pilih model multilingual
    model_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )
    
    client = get_client()
    return client.get_or_create_collection(
        name=collection_name,
        embedding_function=model_func
    )

    # client = get_client()
    # return client.get_or_create_collection(
    #     name=collection_name,
    #     # Optimasi HNSW untuk performa search
    #     metadata={"hnsw:space": "cosine", "hnsw:construction_ef": 128, "hnsw:M": 16}
    # )



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