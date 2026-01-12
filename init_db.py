import chromadb
from db_config import DB_PATH

def initialize_personal_db():
    # Membuat client ke path db_personal
    client = chromadb.PersistentClient(path=DB_PATH)
    
    # Daftar koleksi yang ingin dibuat
    collections = ["japanese_learning", "game_dev", "general"]
    
    print(f"--- Menginisialisasi Database di {DB_PATH} ---")
    for col in collections:
        client.get_or_create_collection(name=col)
        print(f"✅ Koleksi '{col}' siap.")
    
    print("\nInisialisasi selesai!")

if __name__ == "__main__":
    initialize_personal_db()