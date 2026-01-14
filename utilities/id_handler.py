import db_config as db

def check_id_exists(col_name, target_id):
    """Mengecek apakah sebuah ID sudah ada di koleksi ChromaDB."""
    collection = db.get_collection(col_name)
    result = collection.get(ids=[target_id])
    return len(result['ids']) > 0

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