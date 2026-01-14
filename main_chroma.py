import db_config as db
from utilities.insert_data import run_insert
from utilities.delete_data import run_semantic_delete
from utilities.update_data import run_update
from utilities.view_data import run_view_data
from utilities.anki_sync import sync_anki_to_chroma

def semantic_search_flow(col_name):
    collection = db.get_collection(col_name)
    db.clear_screen()
    print(f"--- SEARCH DI [{col_name.upper()}] ---")
    query_text = input("Mau cari informasi apa?: ")
    if not query_text: return
    
    results = collection.query(query_texts=[query_text], n_results=5)

    if not results['ids'] or not results['ids'][0]:
        print("⚠️ Data tidak ditemukan.")
        input("Enter untuk kembali...")
        return

    index = 0
    total = len(results['ids'][0])
    while index < total:
        db.clear_screen()
        print(f"--- HASIL PENCARIAN [{col_name.upper()}] ({index+1}/{total}) ---")
        print(f"ID       : {results['ids'][0][index]}")
        print(f"Konten   : {results['documents'][0][index]}")
        print(f"Metadata : {results['metadatas'][0][index]}")
        print("-" * 45)
        
        print("\nOpsi: [n] Next Result | [b] Back to Menu")
        choice = input("Pilih: ").lower()

        if choice == 'b': break
        elif choice == 'n':
            index += 1
            if index >= total:
                print("🏁 Semua hasil sudah ditampilkan.")
                input("Tekan Enter untuk kembali..."); break

def main():
    while True:
        db.clear_screen()
        collections = db.list_all_collections()
        
        print("============= Chroma DB Dynamic Command Center =============")
        print("1. Tambah Collection Baru")
        print("2. Search In Collection (Quick Search)")
        print("3. Delete From Collection (Quick Delete)")
        print("4. Lihat Seluruh Data (Tabel View)")
        print("5. Sync Anki (Daily Practice)\n")
        
        # Opsi 5 ke atas diisi oleh koleksi yang ada (Offset menjadi 5)
        offset = 6
        for i, name in enumerate(collections):
            print(f"{i + offset}. {name.replace('_', ' ').title()}")
            
        exit_num = len(collections) + offset
        print(f"\n{exit_num}. Keluar")
        
        choice = input(f"\nPilih opsi (1-{exit_num}): ")
        
        if not choice.isdigit(): continue
        choice = int(choice)

        # LOGIKA MENU UTAMA
        if choice == 1:
            new_name = input("Masukkan nama collection baru: ").lower().replace(" ", "_")
            if new_name:
                db.get_collection(new_name)
                print(f"✅ Collection '{new_name}' siap.")
                input("Enter...")

        elif choice in [2, 3, 4, 5]:
            db.clear_screen()
            # Mapping teks untuk menu pemilihan koleksi
            action_map = {2: "SEARCH", 3: "DELETE", 4: "VIEW", 5: "SYNC ANKI"}
            target_action = action_map[choice]
            
            print(f"--- PILIH KOLEKSI UNTUK {target_action} ---")
            for i, c in enumerate(collections): print(f"{i+1}. {c}")
            idx = input("Pilih nomor koleksi: ")
            
            if idx.isdigit() and 0 < int(idx) <= len(collections):
                selected = collections[int(idx)-1]
                if choice == 2: semantic_search_flow(selected)
                elif choice == 3: run_semantic_delete(selected)
                elif choice == 4: run_view_data(selected)
                elif choice == 5: sync_anki_to_chroma(selected)
            # else:
            #     print("⚠️ Pilihan koleksi tidak valid.")
            
            input("\nTekan Enter untuk kembali ke menu utama...")

        elif offset <= choice < exit_num:
            selected_col = collections[choice - offset]
            manage_specific_collection(selected_col)

        elif choice == exit_num:
            print("Sampai jumpa!")
            break

def manage_specific_collection(col_name):
    while True:
        db.clear_screen()
        print(f"=== MANAGE: [{col_name.upper()}] ===")
        print("1. Insert/Sync Data")
        print("2. Search Semantic")
        print("3. Lihat Seluruh Data (Tabel View)") # Juga ditambahkan di sub-menu agar konsisten
        print("4. Update Manual")
        print("5. Delete Semantic")
        print("6. Kembali")
        
        p = input("\nPilih: ")
        if p == "1":
            fname = input("Nama file data: "); run_insert(fname, col_name)
        elif p == "2":
            semantic_search_flow(col_name)
        elif p == "3":
            run_view_data(col_name)
        elif p == "4":
            run_update(col_name)
        elif p == "5":
            run_semantic_delete(col_name)
        elif p == "6":
            break
        input("\nTekan Enter...")

if __name__ == "__main__":
    main()