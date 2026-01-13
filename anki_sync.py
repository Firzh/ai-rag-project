import requests
import json
import db_config as db

ANKI_URL = "http://localhost:8765"

def invoke(action, **params):
    return requests.post(ANKI_URL, json.dumps({"action": action, "version": 6, "params": params})).json()

def sync_anki_optimized(col_name):
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
            all_ids.append(str(note['noteId']))
            all_docs.append(f"Front: {note['fields']['Front']['value']} | Back: {note['fields']['Back']['value']}")
            all_metas.append({"source": "anki", "tags": note['tags']})

        # Optimasi: Kirim dalam satu batch besar
        collection = db.get_collection(col_name)
        collection.upsert(ids=all_ids, documents=all_docs, metadatas=all_metas)
            
        print(f"✅ Berhasil sinkronisasi {len(note_ids)} kartu dari sesi latihan hari ini.")
        
    except requests.exceptions.ConnectionError:
        print("❌ GAGAL: Anki harus dalam keadaan terbuka untuk melakukan sinkronisasi otomatis.")