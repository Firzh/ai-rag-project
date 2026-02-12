import db_config as db
import utilities.anki_sync as anki
import utilities.sanitizer as sanitizer
import utilities.id_handler as id_handler


def run_update(col_name):
    collection = db.get_collection(col_name)
    target_id = input("Masukkan ID yang ingin diupdate: ")
    
    # Cek apakah ID ada
    existing = collection.get(ids=[target_id])
    if not existing['ids']:
        print(f"❌ ID '{target_id}' tidak ditemukan di koleksi {col_name}.")
        return

    print(f"Konten saat ini: {existing['documents'][0]}")
    new_doc = input("Masukkan konten baru: ")
    
    collection.update(ids=[target_id], documents=[new_doc])
    db.clear_screen()
    print(f"✅ Berhasil memperbarui ID {target_id} di [{col_name}]")

def run_migration(collection):
    """
    Migrasi massal data di database ke format Rich Document terbaru.
    Berdasarkan logika penarikan data di anki_sync dan pengujian di central_testing.
    """
    col_name = collection.name
    db.clear_screen()
    collection = db.get_collection(col_name)
    
    # 1. Ambil seluruh data dari database
    print(f"🔍 Menarik seluruh ID dari koleksi [{col_name}]...")
    results = collection.get()
    all_db_ids = results['ids']

    if not all_db_ids:
        print(f"⚠️ Koleksi [{col_name}] kosong. Tidak ada yang perlu dimigrasi.")
        return

    # 2. Filter ID yang berasal dari Anki dan ekstrak Note ID numeriknya
    anki_note_ids = []
    for id_val in all_db_ids:
        if id_val.startswith("anki_"):
            try:
                # Mengubah "anki_12345" menjadi 12345 agar dikenali AnkiConnect
                anki_note_ids.append(int(id_val.replace("anki_", "")))
            except ValueError:
                continue

    if not anki_note_ids:
        print("❌ Tidak ditemukan ID berformat Anki untuk dimigrasi.")
        return

    print(f"📦 Memulai migrasi {len(anki_note_ids)} data...")

    try:
        # 3. Ambil detail konten terbaru dari Anki secara batch
        notes_info = anki.invoke("notesInfo", notes=anki_note_ids)['result']
        
        # Ambil info kartu untuk menghitung ulang maturity/interval
        all_card_ids = []
        for note in notes_info:
            all_card_ids.extend(note['cards'])
        cards_info = anki.invoke("cardsInfo", cards=all_card_ids)['result']
        card_map = {c['cardId']: c for c in cards_info}

        update_ids, update_docs, update_metas = [], [], []
        update_count = 0

        # 4. Transformasi ke format baru
        for note in notes_info:
            f = note['fields']
            # Membangun ulang dokumen dengan format Rich Doc (Arti 1, Kunyomi 1, dll.)
            new_doc = anki.build_rich_doc(f) 
            target_id = f"anki_{note['noteId']}"
            
            # Cek dokumen yang ada saat ini di database
            existing_doc = id_handler.check_id_exists(col_name, target_id)
            
            # Bandingkan apakah formatnya sudah baru atau masih format lama
            if id_handler.is_content_different(existing_doc, new_doc):
                # Hitung ulang metadata (Maturity & Stroke Info)
                note_cards = [card_map.get(cid) for cid in note['cards'] if card_map.get(cid)]
                max_ivl = max([c.get('ivl', 0) for c in note_cards]) if note_cards else 0
                kanji = sanitizer.html_cleaner(f.get('Kanji', {}).get('value', ''))
                stroke_raw = f.get('Stroke number', {}).get('value', '0')

                update_ids.append(target_id)
                update_docs.append(new_doc)
                update_metas.append({
                    "source": "anki",
                    "kanji": kanji,
                    "maturity_interval": max_ivl,
                    "status": "Mature" if max_ivl >= 21 else "Young/Learning",
                    "strokes": sanitizer.html_cleaner(stroke_raw),
                    "stroke_file": sanitizer.extract_svg_filename(stroke_raw),
                    "tags": ", ".join(note['tags'])
                })
                update_count += 1

        # 5. Eksekusi Upsert ke ChromaDB
        if update_ids:
            collection.upsert(ids=update_ids, documents=update_docs, metadatas=update_metas)
            print(f"✅ MIGRASI BERHASIL: {update_count} data diperbarui ke format baru.")
        else:
            print("ℹ️ Semua data sudah menggunakan format terbaru. Tidak ada perubahan dilakukan.")

    except Exception as e:
        print(f"❌ Terjadi kesalahan saat migrasi: {e}")

def main_update(col_name):
    while True:
        db.clear_screen()
        print("=== UPDATE CENTER ===")
        print("1. Update Manual")
        print("2. Migrasi Anki")
        print("0. Kembali ke Menu Utama")
        
        choice = input("\nPilih Uji: ")
        
        if choice == "1": run_update(col_name)
        elif choice == "2": run_migration(col_name)
        elif choice == "0": break
        
        input("\nTekan Enter untuk lanjut...")

if __name__ == "__main__":
    main_update()