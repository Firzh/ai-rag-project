from db_config import get_collection, clear_screen

def run_semantic_delete(col_name):
    collection = get_collection(col_name)
    query_text = input("Cari data yang ingin dihapus (deskripsi/makna): ")
    
    # Cari 1 data terdekat
    results = collection.query(query_texts=[query_text], n_results=1)
    
    if not results['ids'][0]:
        print("⚠️ Data tidak ditemukan.")
        return

    target_id = results['ids'][0][0]
    target_doc = results['documents'][0][0]
    target_meta = results['metadatas'][0][0]

    clear_screen()
    print("--- DATA DITEMUKAN ---")
    print(f"ID       : {target_id}")
    print(f"Konten   : {target_doc}")
    print(f"Metadata : {target_meta}")
    print("----------------------")
    
    confirm = input(f"\nApakah Anda yakin ingin menghapus data ini? (y/n): ").lower()
    
    if confirm == 'y':
        collection.delete(ids=[target_id])
        clear_screen()
        print(f"🗑️ BERHASIL: Data dengan ID {target_id} telah dihapus.")
    else:
        print("❌ Penghapusan dibatalkan.")