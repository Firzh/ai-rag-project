from db_config import get_collection, clear_screen
from utilities.insert_data import run_insert
from utilities.delete_data import run_semantic_delete
from utilities.update_data import run_update

def semantic_search_flow(col_name):
    collection = get_collection(col_name)
    query_text = input("Mau cari informasi apa?: ")
    results = collection.query(query_texts=[query_text], n_results=5)

    if not results['ids'][0]:
        print("⚠️ Data tidak ditemukan."); return

    index = 0
    while index < len(results['ids'][0]):
        clear_screen()
        print(f"--- HASIL PENCARIAN [{col_name.upper()}] (Rank-{index+1}) ---")
        print(f"ID       : {results['ids'][0][index]}")
        print(f"Konten   : {results['documents'][0][index]}")
        print(f"Metadata : {results['metadatas'][0][index]}")
        print("------------------------------------------------")
        
        print("\nOpsi: [b] Kembali ke Menu Utama | [n] Lihat Hasil Berikutnya (Next)")
        choice = input("Pilih: ").lower()

        if choice == 'b': break
        elif choice == 'n':
            index += 1
            if index >= len(results['ids'][0]):
                print("🏁 Semua hasil sudah ditampilkan.")
                input("Tekan Enter..."); break
        else: print("Pilihan tidak valid.")

def main():
    clear_screen()
    print("--- PILIH KATEGORI ---")
    print("1. Japanese Learning\n2. Game Development\n3. General")
    kat = input("Pilih: ")
    col_name = "japanese_learning" if kat == "1" else "game_dev" if kat == "2" else "general"
    
    while True:
        clear_screen()
        print(f"=== DATABASE: [{col_name.upper()}] ===")
        print("1. Insert/Sync File\n2. Semantic Search\n3. Update Manual\n4. Semantic Delete\n5. Ganti Kategori\n6. Keluar")
        
        p = input("\nPilih menu: ")
        if p == "1":
            fname = input("Nama file data: "); run_insert(fname, col_name)
        elif p == "2":
            semantic_search_flow(col_name)
        elif p == "3":
            run_update(col_name)
        elif p == "4":
            run_semantic_delete(col_name)
        elif p == "5":
            main(); break
        elif p == "6":
            break
        input("\nTekan Enter untuk lanjut...")

if __name__ == "__main__":
    main()