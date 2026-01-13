from tabulate import tabulate
import db_config as db

def run_view_data(col_name):
    collection = db.get_collection(col_name)
    
    # Mengambil semua data (tanpa filter)
    results = collection.get()
    
    if not results['ids']:
        print(f"\n⚠️ Koleksi [{col_name.upper()}] masih kosong.")
        return

    # Menyusun data untuk tabel
    table_data = []
    for i in range(len(results['ids'])):
        row = [
            results['ids'][i],
            results['documents'][i],
            str(results['metadatas'][i]) # Meta diubah ke string agar muat di tabel
        ]
        table_data.append(row)

    # Menampilkan tabel
    db.clear_screen()
    print(f"=== ISI KOLEKSI: [{col_name.upper()}] ===")
    print(tabulate(table_data, headers=["ID", "Konten/Dokumen", "Metadata"], tablefmt="grid"))
    print(f"\nTotal Data: {len(results['ids'])}")