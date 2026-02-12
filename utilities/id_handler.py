def check_id_exists(collection, target_id):
    """Mengecek apakah sebuah ID sudah ada menggunakan objek koleksi yang disuntikkan."""
    result = collection.get(ids=[target_id])
    if result['ids']:
        return result['documents'][0]
    return None

def is_content_different(existing_doc, new_doc):
    if not existing_doc:
        return True
    return existing_doc.strip() != new_doc.strip()

def generate_kanji_id(note_id, kanji_char, variation=""):
    clean_kanji = "".join(filter(str.isalnum, kanji_char))
    suffix = f"_{variation}" if variation else ""
    return f"anki_{note_id}_{clean_kanji}{suffix}"