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
    # 1. Jalankan perintah sistem (cls untuk Windows, clear untuk Linux/Mac)
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
        
    # 2. ANSI Escape Codes tingkat lanjut:
    # \033[H  -> Pindah kursor ke posisi awal (baris 1, kolom 1)
    # \033[2J -> Hapus semua karakter yang terlihat di layar
    # \033[3J -> Hapus seluruh scrollback buffer (sejarah teks di atasnya)
    print("\033[H\033[H\033[2J\033[3J", end="", flush=True)