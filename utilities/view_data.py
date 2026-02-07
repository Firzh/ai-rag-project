import db_config as db

def run_view_data(col_name):
    collection = db.get_collection(col_name)
    results = collection.get()
    
    if not results['ids']:
        print(f"\n⚠️ Koleksi [{col_name.upper()}] masih kosong.")
        return

    total_data = len(results['ids'])
    current_index = 0
    items_per_page = 1 # Menampilkan 1 "Kartu" per halaman agar fokus

    while True:
        db.clear_screen()
        # Ambil potongan data berdasarkan index dan page size
        end_index = min(current_index + items_per_page, total_data)
        print(f"=== BROWSER DATA: [{col_name.upper()}] ===")
        print(f"Menampilkan {current_index + 1} dari {total_data} data\n")
        
        # Ambil data spesifik
        for idx in range(current_index, end_index):
            id_val = results['ids'][idx]
            doc_val = results['documents'][idx]
            meta_val = results['metadatas'][idx]

            # Tampilan ala Kartu (Simple UI)
            print(f"┏━━━━ ID: {id_val} ━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"┃")
            
            # Cetak isi dokumen baris per baris
            for line in doc_val.split('\n'):
                print(f"┃  {line}")
                
            print(f"┃")
            print(f"┣━━━━ METADATA ━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            for key, val in meta_val.items():
                print(f"┃  {key}: {val}")
            print(f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            print("\nNavigasi: [n] Next | [p] Previous | [q] Keluar")
            cmd = input("Pilih: ").lower()

            if cmd == 'n':
                if current_index + 1 < total_data: current_index += 1
            elif cmd == 'p':
                if current_index > 0: current_index -= 1
            elif cmd == 'q':
                break