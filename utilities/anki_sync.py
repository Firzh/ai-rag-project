import requests
import json
import db_config as db
from utilities.sanitizer import clean_html

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
            rich_doc = (
                f"Kanji: {kanji}\n"
                f"Arti: {meanings}\n"
                f"Kunyomi: {kun_reading}\n"
                f"Onyomi: {on_reading}\n"
                f"Mnemonic: {mnemonic}\n"
                f"Contoh Kata: {words}"
            )
            
            # 3. Masukkan ke List jika Kanji dan Arti ada
            if kanji and meanings:
                all_ids.append(f"anki_{note['noteId']}")
                all_docs.append(rich_doc)
                all_metas.append({
                    "source": "anki",
                    "kanji": kanji,
                    "strokes": f.get('Stroke number', {}).get('value', '0'),
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
    """Membangun dokumen hanya dari field yang memiliki isi."""
    lines = []
    labels = {
        'Kanji': 'Kanji',
        'Meanings': 'Arti',
        'Kunyomi': 'Kun',
        'Onyomi': 'On',
        'Mnemonic': 'Cerita/Mnemonic',
        'Words': 'Contoh'
    }
    
    for key, label in labels.items():
        val = clean_html(fields_dict.get(key, {}).get('value', ''))
        if val: # Hanya tambahkan jika ada isinya
            lines.append(f"{label}: {val}")
            
    return "\n".join(lines)