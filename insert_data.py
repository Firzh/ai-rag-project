from db_config import get_collection
from dummy_data import KANJI_DATA

def run_insert():
    collection = get_collection()
    
    # Ekstraksi data dari dummy_data.py
    documents = [item["doc"] for item in KANJI_DATA]
    metadatas = [item["meta"] for item in KANJI_DATA]
    ids = [item["id"] for item in KANJI_DATA]
    
    collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
    print(f"✅ Berhasil memasukkan {len(ids)} data dari dummy_data.py")

if __name__ == "__main__":
    run_insert()