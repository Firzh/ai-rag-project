import requests
import json
import db_config as db
from utilities.sanitizer import clean_html
from utilities.sanitizer import extract_svg_filename

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
        all_ids, all_docs, all_metas = [], [], []
        
        for note in notes_info:
            # DEBUG: Ambil semua nama field yang tersedia di kartu ini
            available_fields = list(note['fields'].keys())

            f = note['fields']

            # 1. Ekstraksi field berdasarkan hasil debug
            kanji = clean_html(f.get('Kanji', {}).get('value', ''))
            meanings = clean_html(f.get('Meanings', {}).get('value', ''))
            on_reading = clean_html(f.get('Onyomi', {}).get('value', ''))
            kun_reading = clean_html(f.get('Kunyomi', {}).get('value', ''))
            mnemonic = clean_html(f.get('Mnemonic', {}).get('value', ''))
            words = clean_html(f.get('Words', {}).get('value', ''))

            # 2. Bangun Document "Rich Context" (Agar Semantic Search Pintar)
            # Kita buat format yang rapi agar model L12 paham hubungannya
            rich_doc = build_rich_doc(f)
            
            # 3. Masukkan ke List jika Kanji dan Arti ada
            if kanji and meanings:
                all_ids.append(f"anki_{note['noteId']}")
                all_docs.append(rich_doc)

                stroke_raw = f.get('Stroke number', {}).get('value', '0')
                all_metas.append({
                    "source": "anki",
                    "kanji": kanji,
                    "strokes": clean_html(stroke_raw), # Simpan hanya angkanya
                    "stroke_file": extract_svg_filename(stroke_raw), # Simpan referensi SVG
                    "tags": ", ".join(note['tags'])
                })
            else:
                # Log jika field tidak ditemukan
                print(f"⚠️ Warning: Kartu ID {note['noteId']} dilewati. ")
                print(f"   Field yang tersedia: {available_fields}")

        if not all_ids:
            print("\n⚠️ GAGAL: Kartu terdeteksi tapi field tidak sesuai template.")
            return
        
        # Upsert ke ChromaDB menggunakan model L12 Multilingual
        collection = db.get_collection(col_name)
        collection.upsert(ids=all_ids, documents=all_docs, metadatas=all_metas)
        
        # db.clear_screen()
        print(f"✅ BERHASIL: {len(all_ids)} kartu Anki telah disinkronkan ke [{col_name.upper()}]")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Anki tidak terdeteksi. Pastikan aplikasi Anki sudah terbuka.")
    except Exception as e:
        print(f"\n❌ ERROR Sinkronisasi: {e}")

def build_rich_doc(fields_dict):
    lines = []
    
    # 1. Kanji (Label Eksplisit)
    kanji = clean_html(fields_dict.get('Kanji', {}).get('value', ''))
    if kanji: lines.append(f"Kanji: {kanji}")

    # 2. Arti dengan Increment List
    raw_meanings = fields_dict.get('Meanings', {}).get('value', '')

    # Gunakan preserve_newline=True agar <div> terpisah jadi baris baru
    clean_meanings = clean_html(raw_meanings, preserve_newline=True)
    if clean_meanings:
        meaing_list = clean_meanings.split('\n')
        for i, arti in enumerate(meaing_list, 1):
            lines.append(f"Arti {i}: {arti}")
    
    # 3. Bacaan Deskriptif untuk AI
    kun = clean_html(fields_dict.get('Kunyomi', {}).get('value', ''))
    on = clean_html(fields_dict.get('Onyomi', {}).get('value', ''))
    if kun: lines.append(f"Kunyomi (Reading Jepang): {kun}")
    if on: lines.append(f"Onyomi (Reading Cina): {on}")

    # 4. Contoh Kotoba
    raw_words = fields_dict.get('Words', {}).get('value', '')
    clean_words = clean_html(raw_words, preserve_newline=True)
    if clean_words:
        words_packages = clean_words.split('\n')
        for i, pkg in enumerate(words_packages, 1):
            # Di sini satu baris sudah berisi "Kanji / Reading - Meaning"
            lines.append(f"Contoh: {i}, {pkg}")

    # 5. Mnemonic
    mnem = clean_html(fields_dict.get('Mnemonic', {}).get('value', ''))
    if mnem: lines.append(f"Cerita/Mnemonic: {mnem}")

def test_numbering():
    print("\n--- [TEST] VERIFIKASI PENOMORAN CONTOH ---")
    
    final_doc = build_rich_doc()
    print("Hasil Konstruksi Dokumen:")
    print("-" * 20)
    print(final_doc)
    print("-" * 20)
    
    if "Contoh 3:" in final_doc:
        print("✅ Berhasil: Contoh dipisah menjadi Contoh 1, 2, dan 3.")
    else:
        print("❌ Gagal: Contoh masih menyatu.")