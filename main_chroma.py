import db_config as db
import utilities.update_data as update
import utilities.delete_data as delete
import utilities.anki_sync as anki_sync
import utilities.sanitizer as sanitizer
import utilities.id_handler as id_handler
from utilities.central_testing import main_test
from utilities.insert_data import run_insert
from utilities.view_data import run_view_data

# 2. Re-use anki_invoker (atau buat fungsi global di main_chroma agar efisien)
def anki_invoker(action, **params):
    import requests, json
    ANKI_URL = "http://localhost:8765"
    try:
        return requests.post(ANKI_URL, data=json.dumps({"action": action, "version": 6, "params": params})).json()
    except:
        return {"result": None, "error": "Anki is closed"}

def handle_sync(selected_col_name):
    """Fungsi buffer untuk menyiapkan Dependency Injection"""
    # 1. Ubah string nama menjadi objek Koleksi
    target_collection = db.get_collection(selected_col_name)
    
    # 3. Suntikkan semua dependensi ke dalam fungsi inti
    anki_sync.sync_anki_to_chroma(
        collection=target_collection,
        anki_invoker=anki_invoker,
        sanitizer_tool=sanitizer,
        id_tool=id_handler
    )
    
def handle_update_center(selected_col_name):
    """Fungsi jembatan untuk menyuntikkan semua dependensi ke Update Center."""
    # 1. Siapkan objek Koleksi
    target_collection = db.get_collection(selected_col_name)

    # 3. Panggil main_update dengan menyuntikkan SEMUA dependensi
    update.main_update(
        collection=target_collection,
        anki_invoker=anki_invoker,
        anki_tools=anki_sync,  # anki_sync mengandung fungsi build_rich_doc
        sanitizer_tool=sanitizer,
        id_tool=id_handler,
        ui_tool=db            # db_config digunakan untuk clear_screen
    )

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
        
        print("============= Chroma DB Dynamic Command Center =============")
        print("1. Tambah Collection Baru")
        print("2. Search In Collection")
        print("3. Delete From Collection")
        print("4. Tabel View Collection")
        print("5. Sync Anki")
        print("6. Testing")
        print("7. List of Collections")
        print("0. Keluar")
        
        choice = input("\nPilih opsi (0-7): ")
        
        if not choice.isdigit(): continue
        choice = int(choice)

        # 1. TAMBAH KOLEKSI
        if choice == 1:
            new_name = input("Masukkan nama collection baru: ").lower().replace(" ", "_")
            if new_name:
                db.get_collection(new_name)
                print(f"✅ Collection '{new_name}' siap.")
                input("Enter...")

        # 2-6. AKSI GENERIC (Tetap menggunakan flow pilih koleksi di dalam)
        elif choice in [2, 3, 4, 5, 6]:
            collections = db.list_all_collections()
            db.clear_screen()
            action_map = {2: "SEARCH", 3: "DELETE", 4: "VIEW", 5: "SYNC ANKI", 6: "TESTING"}
            target_action = action_map[choice]
            
            print(f"--- PILIH KOLEKSI UNTUK {target_action} ---")
            for i, c in enumerate(collections): print(f"{i+1}. {c}")
            idx = input("Pilih nomor koleksi: ")
            
            if idx.isdigit() and 0 < int(idx) <= len(collections):
                selected = collections[int(idx)-1]
                if choice == 2: semantic_search_flow(selected)
                elif choice == 3: delete.main_delete(selected)
                elif choice == 4: run_view_data(selected)
                elif choice == 5: handle_sync(selected)
                elif choice == 6: main_test()
                else:
                    print("⚠️ Pilihan koleksi tidak valid.")
                input("\nTekan Enter untuk kembali...")

        # 7. MANAGE SPECIFIC COLLECTION (Sub-Menu Baru)
        elif choice == 7:
            collections = db.list_all_collections()
            db.clear_screen()
            print("--- DAFTAR KOLEKSI TERSEDIA ---")
            for i, name in enumerate(collections):
                print(f"{i + 1}. {name.replace('_', ' ').title()}")
            
            print(f"0. Kembali")
            
            idx = input("\nPilih koleksi yang ingin dikelola: ")
            if idx.isdigit():
                idx_int = int(idx)
                if 0 < idx_int <= len(collections):
                    selected_col = collections[idx_int - 1]
                    manage_specific_collection(selected_col) # Pindah ke menu internal koleksi
                elif idx_int == 0:
                    continue

        # 8. KELUAR
        elif choice == 0:
            print("Sampai jumpa!")
            db.clear_screen()
            break

def manage_specific_collection(col_name):
    while True:
        db.clear_screen()
        print(f"=== MANAGE: [{col_name.upper()}] ===")
        print("1. Insert Data")
        print("2. Search Semantic")
        print("3. Lihat Seluruh Data (Tabel View)")
        print("4. Update Data")
        print("5. Delete Data")

        print("0. Kembali")
        
        p = input("\nPilih: ")
        if p == "1":
            fname = input("Nama file data: "); run_insert(fname, col_name)
        elif p == "2":
            semantic_search_flow(col_name)
        elif p == "3":
            run_view_data(col_name)
        elif p == "4":
            handle_update_center(col_name)
        elif p == "5":
            delete.main_delete(col_name)
        elif p == "0":
            break
        input("\nTekan Enter...")

if __name__ == "__main__":
    main()