from db_config import get_collection, clear_screen

def run_update(col_name):
    collection = get_collection(col_name)
    target_id = input("Masukkan ID yang ingin diupdate: ")
    
    # Cek apakah ID ada
    existing = collection.get(ids=[target_id])
    if not existing['ids']:
        print(f"❌ ID '{target_id}' tidak ditemukan di koleksi {col_name}.")
        return

    print(f"Konten saat ini: {existing['documents'][0]}")
    new_doc = input("Masukkan konten baru: ")
    
    collection.update(ids=[target_id], documents=[new_doc])
    clear_screen()
    print(f"✅ Berhasil memperbarui ID {target_id} di [{col_name}]")