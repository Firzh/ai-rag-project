import db_config as db

def check_id_exists(col_name, target_id):
    """Mengecek apakah sebuah ID sudah ada di koleksi ChromaDB."""
    collection = db.get_collection(col_name)
    result = collection.get(ids=[target_id])
    if result['ids']:
        # Mengembalikan dokumen pertama yang ditemukan
        return result['documents'][0]
    return None

def is_content_different(existing_doc, new_doc):
    """
    Membandingkan dokumen lama dan baru.
    Mengembalikan True jika ada perubahan.
    """
    
    if not existing_doc:
        return True # Jika tidak ada data lama, dianggap berbeda (perlu insert)
    
    # Menghapus spasi putih berlebih di awal/akhir untuk perbandingan adil
    return existing_doc.strip() != new_doc.strip()

def generate_kanji_id(note_id, kanji_char, variation=""):
    """
    Membuat ID unik yang deskriptif.
    Format: anki_[noteId]_[Kanji]_[Varian]
    Contoh: anki_175829_水_v2
    """
    # Menghapus karakter yang mungkin bermasalah jika ada
    clean_kanji = "".join(filter(str.isalnum, kanji_char))
    suffix = f"_{variation}" if variation else ""
    return f"anki_{note_id}_{clean_kanji}{suffix}"