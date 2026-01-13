import importlib
from db_config import get_collection, clear_screen

def run_insert(file_name, col_name):
    try:
        # Load modul secara dinamis berdasarkan input user
        data_module = importlib.import_module(f"data.{file_name}")
        data_to_insert = data_module.DATA_LIST
        
        collection = get_collection(col_name)
        
        ids = [item["id"] for item in data_to_insert]
        docs = [item["doc"] for item in data_to_insert]
        metas = [item["meta"] for item in data_to_insert]
        
        collection.upsert(ids=ids, documents=docs, metadatas=metas)
        
        clear_screen()
        print(f"✅ SUKSES: Berhasil menginput {len(ids)} data dari '{file_name}'")
    except ModuleNotFoundError:
        print(f"❌ ERROR: File '{file_name}.py' tidak ditemukan.")
    except Exception as e:
        print(f"❌ ERROR: Terjadi kesalahan: {e}")