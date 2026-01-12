import os
from insert_data import run_insert
from update_data import run_update
from delete_data import run_delete
from db_config import get_collection

def main():
    while True:
        print("\n=== CHROMA DB COMMAND CENTER ===")
        print("1. Insert/Sync Data (dari dummy_data.py)")
        print("2. Cari Data (Semantic Search)")
        print("3. Update Data Manual")
        print("4. Hapus Data")
        print("5. Keluar")
        
        pilihan = input("Pilih menu (1-5): ")

        if pilihan == "1":
            run_insert()
        elif pilihan == "2":
            query = input("Masukkan keyword pencarian: ")
            collection = get_collection()
            res = collection.query(query_texts=[query], n_results=1)
            print(f"\nHasil: {res['documents'][0]}")
        elif pilihan == "3":
            target_id = input("Masukkan ID yang akan diupdate: ")
            new_doc = input("Masukkan konten baru: ")
            run_update(target_id, new_doc)
        elif pilihan == "4":
            target_id = input("Masukkan ID yang akan dihapus: ")
            run_delete(target_id)
        elif pilihan == "5":
            print("Sampai jumpa!")
            break
        else:
            print("Pilihan tidak valid.")

if __name__ == "__main__":
    main()