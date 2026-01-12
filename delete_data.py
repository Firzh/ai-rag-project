# delete_data.py
from db_config import get_collection

def run_delete(target_id):
    collection = get_collection()
    collection.delete(ids=[target_id])
    print(f"🗑️ Data {target_id} berhasil dihapus.")