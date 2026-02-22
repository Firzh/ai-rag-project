
def run_update(collection):
    """Update konten secara manual menggunakan objek koleksi yang disuntikkan."""
    target_id = input("Masukkan ID yang ingin diupdate: ")
    
    # Cek apakah ID ada langsung melalui objek collection
    existing = collection.get(ids=[target_id])
    if not existing['ids']:
        print(f"❌ ID '{target_id}' tidak ditemukan di koleksi.")
        return

    print(f"Konten saat ini: {existing['documents'][0]}")
    new_doc = input("Masukkan konten baru: ")
    
    collection.update(ids=[target_id], documents=[new_doc])
    print(f"✅ Berhasil memperbarui ID {target_id}")

def run_migration(collection, anki_invoker, anki_tools, sanitizer_tool, id_tool):
    """
    Migrasi massal menggunakan Dependency Injection penuh.
    - collection: Objek koleksi dari db_config
    - anki_invoker: Fungsi invoke untuk AnkiConnect
    - anki_tools: Modul/Objek yang memiliki build_rich_doc
    - sanitizer_tool: Modul sanitizer
    - id_tool: Modul id_handler
    """
    print(f"🔍 Menarik seluruh ID dari koleksi [{collection.name}]...")
    results = collection.get()
    all_db_ids = results['ids']

    if not all_db_ids:
        print(f"⚠️ Koleksi [{collection.name}] kosong. Tidak ada yang perlu dimigrasi.")
        return

    anki_note_ids = []
    for id_val in all_db_ids:
        if id_val.startswith("anki_"):
            try:
                anki_note_ids.append(int(id_val.replace("anki_", "")))
            except ValueError:
                continue

    if not anki_note_ids:
        print("❌ Tidak ditemukan ID berformat Anki untuk dimigrasi.")
        return

    print(f"📦 Memulai migrasi {len(anki_note_ids)} data...")

    try:
        # Menggunakan invoker yang disuntikkan
        notes_info = anki_invoker("notesInfo", notes=anki_note_ids)['result']
        
        all_card_ids = []
        for note in notes_info:
            all_card_ids.extend(note['cards'])
        cards_info = anki_invoker("cardsInfo", cards=all_card_ids)['result']
        card_map = {c['cardId']: c for c in cards_info}

        update_ids, update_docs, update_metas = [], [], []
        update_count = 0

        for note in notes_info:
            f = note['fields']
            # build_rich_doc sekarang butuh sanitizer sebagai dependensi
            new_doc = anki_tools.build_rich_doc(f, sanitizer_tool) 
            target_id = f"anki_{note['noteId']}"
            
            # id_handler sekarang butuh objek koleksi, bukan string nama
            existing_doc = id_tool.check_id_exists(collection, target_id)
            
            if id_tool.is_content_different(existing_doc, new_doc):
                note_cards = [card_map.get(cid) for cid in note['cards'] if card_map.get(cid)]
                max_ivl = max([c.get('ivl', 0) for c in note_cards]) if note_cards else 0
                
                # Gunakan sanitizer yang disuntikkan
                kanji = sanitizer_tool.html_cleaner(f.get('Kanji', {}).get('value', ''))
                stroke_raw = f.get('Stroke number', {}).get('value', '0')

                update_ids.append(target_id)
                update_docs.append(new_doc)
                update_metas.append({
                    "source": "anki",
                    "kanji": kanji,
                    "maturity_interval": max_ivl,
                    "status": "Mature" if max_ivl >= 21 else "Young/Learning",
                    "strokes": sanitizer_tool.html_cleaner(stroke_raw),
                    "stroke_file": sanitizer_tool.extract_svg_filename(stroke_raw),
                    "tags": ", ".join(note['tags'])
                })
                update_count += 1

        if update_ids:
            collection.upsert(ids=update_ids, documents=update_docs, metadatas=update_metas)
            print(f"✅ MIGRASI BERHASIL: {update_count} data diperbarui.")
        else:
            print("ℹ️ Semua data sudah menggunakan format terbaru.")

    except Exception as e:
        print(f"❌ Terjadi kesalahan saat migrasi: {e}")

def main_update(collection, anki_invoker, anki_tools, sanitizer_tool, id_tool, ui_tool):
    """Titik masuk menu update dengan suntikan dependensi UI."""
    while True:
        ui_tool.clear_screen() # Suntikan db_config sebagai ui_tool
        print(f"=== UPDATE CENTER: [{collection.name.upper()}] ===")
        print("1. Update Manual")
        print("2. Migrasi Anki")
        print("0. Kembali")
        
        choice = input("\nPilih: ")
        if choice == "1": 
            run_update(collection)
        elif choice == "2": 
            run_migration(collection, anki_invoker, anki_tools, sanitizer_tool, id_tool)
        elif choice == "0": 
            break
        input("\nTekan Enter untuk lanjut...")