import requests
import json
import db_config as db
import utilities.sanitizer as sanitizer
import utilities.id_handler as id_handler

ANKI_URL = "http://localhost:8765"

def invoke(action, **params):
    return requests.post(ANKI_URL, json.dumps({"action": action, "version": 6, "params": params})).json()

def sync_anki_to_chroma(col_name):
    # 1. Cek apakah Anki terbuka
    try:
        # 2. Cari kartu yang dipelajari/diubah dalam 24 jam terakhir
        # Query 'rated:1' artinya mencari kartu yang dijawab hari ini
        note_ids = invoke("findNotes", query="rated:1")['result']
        
        if not note_ids:
            print("ℹ️ Tidak ada sesi latihan baru hari ini.")
            return

        # 3. Ambil detail konten kartu
        notes_info = invoke("notesInfo", notes=note_ids)['result']
        
        # Ambil semua card_ids untuk batch processing maturity
        all_card_ids = []
        for note in notes_info:
            all_card_ids.extend(note['cards'])
        cards_info = invoke("cardsInfo", cards = all_card_ids)['result']
        card_map = {cards['cardId']: cards for cards in cards_info}

        all_ids, all_docs, all_metas = [], [], []
        
        for note in notes_info:
            # DEBUG: Ambil semua nama field yang tersedia di kartu ini
            # available_fields = list(note['fields'].keys())

            f = note['fields']

            # Ekstraksi minimal untuk validasi dan metadata
            kanji = sanitizer.html_cleaner(f.get('Kanji', {}).get('value', ''))
            meanings = sanitizer.html_cleaner(f.get('Meanings', {}).get('value', ''))
          
            if kanji and meanings:

                # Document "Rich Context" (Agar Semantic Search Pintar)
                new_doc = build_rich_doc(f)
                target_id = f"anki_{note['noteId']}"

                # Cek id dan perbandingan isi
                existing_doc = id_handler.check_id_exists(col_name, target_id)

                if id_handler.is_content_different(existing_doc, new_doc):
                    # Hitung Kematangan (Maturity)
                    # Anki menggunakan 'ivl' (interval). ivl >= 21 hari dianggap "Mature"
                    note_cards = [card_map.get(cid) for cid in note['cards'] if card_map.get(cid)]
                    max_ivl = max([c.get('ivl', 0) for c in note_cards]) if note_cards else 0 

                    all_ids.append(target_id)
                    all_docs.append(new_doc)

                    stroke_raw = f.get('Stroke number', {}).get('value', '0')
                    all_metas.append({
                        "source": "anki",
                        "kanji": kanji,
                        "maturity_interval": max_ivl,
                        "status": "Mature" if max_ivl >= 21 else "Young/Learning",
                        "strokes": sanitizer.html_cleaner(stroke_raw),                # Simpan hanya angkanya
                        "stroke_file": sanitizer.extract_svg_filename(stroke_raw),    # Simpan referensi SVG
                        "tags": ", ".join(note['tags'])
                    })
                    update_count += 1
                else:
                    skip_count += 1
            else:
                # Log jika field tidak ditemukan
                print(f"⚠️ Warning: Kartu ID {note['noteId']} dilewati. ")
                # print(f"   Field yang tersedia: {available_fields}")

        if all_ids:
            collection = db.get_collection(col_name)
            collection.upsert(ids=all_ids, documents=all_docs, metadatas=all_metas)
            print(f"✅ SYNC SELESAI: {update_count} data diupdate, {skip_count} data identik diabaikan.")
        else:
            print(f"ℹ️ Semua data ({skip_count} kartu) sudah up-to-date di [{col_name.upper()}].")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Anki tidak terdeteksi. Pastikan aplikasi Anki sudah terbuka.")
    except Exception as e:
        print(f"\n❌ ERROR Sinkronisasi: {e}")

def build_rich_doc(fields_dict):

    def add_incremental(field_name, label):
        raw = fields_dict.get(field_name, {}).get('value', '')
        clean = sanitizer.html_cleaner(raw, preserve_newline=True)
        if clean:
            items = clean.split('\n')
            for i, item in enumerate(items, 1):
                lines.append(f"{label} {i}: {item}")
    
    def add_non_incremental(field_name, label):
        item = sanitizer.html_cleaner(fields_dict.get(field_name, {}).get('value', ''))
        if item: lines.append(f"{label}: {item}")

    lines = []
    
    # 1. Kanji
    add_non_incremental('Kanji', 'Kanji')

    # 2. Field dengan Increment List
    add_incremental('Meanings', 'Arti')
    add_incremental('Kunyomi', 'Kunyomi')
    add_incremental('Onyomi', 'Onyomi')
    add_incremental('Nanori', 'Nanori')
    add_incremental('Words', 'Contoh')

    # 5. Mnemonic
    add_non_incremental('Mnemonic', 'Cerita/Mnemonic')

    return "\n".join(lines)