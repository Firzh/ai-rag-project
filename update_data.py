# update_data.py
from db_config import get_collection

def run_update(target_id, new_doc):
    collection = get_collection()
    collection.update(ids=[target_id], documents=[new_doc])
    print(f"✅ Data {target_id} berhasil diperbarui.")
