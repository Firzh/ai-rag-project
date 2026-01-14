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

def run_clear_collection(col_name):
    """Menghapus seluruh data dalam satu koleksi."""
    collection = get_collection(col_name)
    count = collection.count()
    
    if count == 0:
        print(f"⚠️ Koleksi [{col_name.upper()}] sudah kosong.")
        return

    print(f"❗ PERINGATAN: Anda akan menghapus SELURUH data ({count} item) di [{col_name.upper()}].")
    confirm = input("Ketik 'YAKIN' untuk melanjutkan: ")
    
    if confirm == 'YAKIN':
        # Mengambil semua ID untuk dihapus
        all_ids = collection.get()['ids']
        collection.delete(ids=all_ids)
        print(f"🔥 BERHASIL: Koleksi [{col_name.upper()}] dikosongkan.")
    else:
        print("❌ Pembatalan dilakukan.")

def run_batch_delete(col_name):
    """Mencari 10 data mirip dan memilih yang ingin dihapus."""
    collection = get_collection(col_name)
    query = input("Cari hal mirip yang ingin di-batch delete: ")
    res = collection.query(query_texts=[query], n_results=10)
    
    if not res['ids'][0]:
        print("⚠️ Tidak ada data ditemukan."); return

    ids = res['ids'][0]
    docs = res['documents'][0]
    
    print(f"\n--- HASIL PENCARIAN (Pilih nomor untuk dihapus) ---")
    for i in range(len(ids)):
        print(f"[{i+1}] ID: {ids[i]} | Konten: {docs[i][:80]}...")

    selection = input("\nMasukkan nomor yang ingin dihapus (contoh: 1,3,5) atau '0' untuk batal: ")
    if selection == '0' or not selection: return

    try:
        # Parsing input user (e.g. "1,3" -> [ids[0], ids[2]])
        indices = [int(x.strip()) - 1 for x in selection.split(',')]
        target_ids = [ids[i] for i in indices if 0 <= i < len(ids)]
        
        print(f"Target hapus: {len(target_ids)} data.")
        confirm = input("Konfirmasi hapus? (y/n): ").lower()
        if confirm == 'y':
            collection.delete(ids=target_ids)
            print(f"🗑️ BERHASIL: {len(target_ids)} data dihapus.")
    except Exception as e:
        print(f"❌ Input tidak valid: {e}")