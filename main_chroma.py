from db_config import get_collection, clear_screen
from Utilities.insert_data import run_insert
from Utilities.delete_data import run_semantic_delete

def main():
    clear_screen()
    # Pilihan koleksi awal
    print("--- PILIH KATEGORI PERSONALISASI ---")
    print("1. Japanese Learning")
    print("2. Game Development")
    print("3. General/Lainnya")
    kat = input("Pilih (1-3): ")
    
    col_name = "japanese_learning" if kat == "1" else "game_dev" if kat == "2" else "general"
    
    current_collection = get_collection(col_name)
    clear_screen()

    while True:
        print(f"\n=== COMMAND CENTER: [{col_name.upper()}] ===")
        print("1. Insert Data (Pilih File)")
        print("2. Cari Data (Semantic Search)")
        print("3. Hapus Data (Semantic Search)")
        print("4. Ganti Kategori")
        print("5. Keluar")
        
        pilihan = input("\nPilih menu (1-5): ")

        if pilihan == "1":
            file_name = input("Masukkan nama file data (misal: data_kanji): ")
            # Pastikan fungsi run_insert di file lain menerima col_name
            run_insert(file_name, col_name) 
        elif pilihan == "2":
            query = input("Cari apa hari ini?: ")
            res = current_collection.query(query_texts=[query], n_results=1)
            clear_screen()
            if res['documents'][0]:
                print(f"Hasil Terkait:\n> {res['documents'][0][0]}")
            else:
                print("Data tidak ditemukan.")
        elif pilihan == "3":
            run_semantic_delete(col_name)
        elif pilihan == "4":
            main() # Kembali ke pemilihan kategori
            break
        elif pilihan == "5":
            print("Shutting down...")
            break