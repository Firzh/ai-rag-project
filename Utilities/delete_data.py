from db_config import get_collection, clear_screen

def run_semantic_delete(col_name):
    collection = get_collection(col_name)
    query_text = input("Cari data yang ingin dihapus: ")
    
    # Ambil 5 hasil terdekat untuk fitur 'Next'
    results = collection.query(query_texts=[query_text], n_results=5)
    
    if not results['ids'][0]:
        print("⚠️ Tidak ada data yang mirip.")
        return

    index = 0
    while index < len(results['ids'][0]):
        target_id = results['ids'][0][index]
        target_doc = results['documents'][0][index]
        target_meta = results['metadatas'][0][index]

        clear_screen()
        print(f"--- KONFIRMASI HAPUS [{col_name.upper()}] (Hasil ke-{index+1}) ---")
        print(f"ID       : {target_id}")
        print(f"Konten   : {target_doc}")
        print(f"Metadata : {target_meta}")
        print("------------------------------------------------")
        
        print("\nOpsi: [y] Ya, Hapus | [n] Bukan ini (Next) | [c] Batal/Cancel")
        choice = input("Pilih: ").lower()

        if choice == 'y':
            collection.delete(ids=[target_id])
            clear_screen()
            print(f"🗑️ BERHASIL: {target_id} dihapus.")
            break
        elif choice == 'n':
            index += 1
            if index >= len(results['ids'][0]):
                print("🏁 Sudah mencapai batas hasil pencarian.")
                input("Tekan Enter untuk kembali..."); break
        elif choice == 'c':
            print("❌ Penghapusan dibatalkan.")
            break