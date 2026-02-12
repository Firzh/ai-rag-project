def sync_anki_to_chroma(collection, anki_invoker, sanitizer_tool, id_tool):
    """
    Sinkronisasi dengan Dependency Injection penuh.
    - collection: Objek koleksi ChromaDB
    - anki_invoker: Fungsi untuk memanggil AnkiConnect (misal: invoke)
    - sanitizer_tool: Modul atau objek yang berisi fungsi pembersih HTML
    - id_tool: Modul atau objek untuk manajemen ID dan komparasi isi
    """
    try:
        # Menggunakan invoker yang disuntikkan
        note_ids = anki_invoker("findNotes", query="rated:1")['result']
        
        if not note_ids:
            print("ℹ️ Tidak ada sesi latihan baru hari ini.")
            return

        notes_info = anki_invoker("notesInfo", notes=note_ids)['result']
        
        all_card_ids = []
        for note in notes_info:
            all_card_ids.extend(note['cards'])
        
        cards_info = anki_invoker("cardsInfo", cards=all_card_ids)['result']
        card_map = {cards['cardId']: cards for cards in cards_info}

        all_ids, all_docs, all_metas = [], [], []
        update_count = 0 
        skip_count = 0
        
        for note in notes_info:
            f = note['fields']

            # Menggunakan sanitizer_tool yang disuntikkan
            kanji = sanitizer_tool.html_cleaner(f.get('Kanji', {}).get('value', ''))
            meanings = sanitizer_tool.html_cleaner(f.get('Meanings', {}).get('value', ''))
          
            if kanji and meanings:
                # build_rich_doc sekarang juga membutuhkan sanitizer_tool
                new_doc = build_rich_doc(f, sanitizer_tool)
                target_id = f"anki_{note['noteId']}"

                # Menggunakan id_tool yang disuntikkan
                existing_doc = id_tool.check_id_exists(collection, target_id)

                if id_tool.is_content_different(existing_doc, new_doc):
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
                        "strokes": sanitizer_tool.html_cleaner(stroke_raw),
                        "stroke_file": sanitizer_tool.extract_svg_filename(stroke_raw),
                        "tags": ", ".join(note['tags'])
                    })
                    update_count += 1
                else:
                    skip_count += 1
            else:
                print(f"⚠️ Warning: Kartu ID {note['noteId']} dilewati.")

        if all_ids:
            # Operasi upsert langsung pada objek koleksi
            collection.upsert(ids=all_ids, documents=all_docs, metadatas=all_metas)
            print(f"✅ SYNC SELESAI: {update_count} data diupdate.")
        else:
            print(f"ℹ️ Semua data sudah up-to-date di [{collection.name.upper()}].")
        
    except Exception as e:
        print(f"\n❌ ERROR Sinkronisasi: {e}")


def build_rich_doc(fields_dict, sanitizer):
    """Menerima sanitizer sebagai dependency."""
    lines = []
    
    def add_incremental(field_name, label, split_regex=None):
        field_obj = fields_dict.get(field_name)
        raw = field_obj.get('value', 'null') if field_obj else 'null'
        
        # Menggunakan sanitizer yang disuntikkan
        clean = sanitizer.html_cleaner(raw, preserve_newline=True)
        
        if not clean or clean == 'null':
            lines.append(f"{label} 1: null")
            return

        import re
        items = re.split(split_regex, clean) if split_regex else clean.split('\n')
        
        count = 1
        for item in items:
            text = item.strip()
            if text:
                lines.append(f"{label} {count}: {text}")
                count += 1

    def add_non_incremental(field_name, label):
        field_obj = fields_dict.get(field_name)
        val = field_obj.get('value', 'null') if field_obj else 'null'
        clean = sanitizer.html_cleaner(val)
        lines.append(f"{label}: {clean if clean else 'null'}")

    add_non_incremental('Kanji', 'Kanji')
    add_incremental('Meanings', 'Arti')
    
    reading_split = r'[\n,、]' 
    add_incremental('Kunyomi', 'Kunyomi', split_regex=reading_split)
    add_incremental('Onyomi', 'Onyomi', split_regex=reading_split)
    add_incremental('Nanori', 'Nanori', split_regex=reading_split)
    add_incremental('Words', 'Contoh')
    add_non_incremental('Mnemonic', 'Cerita/Mnemonic')

    return "\n".join(lines)