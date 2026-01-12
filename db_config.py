import chromadb

def get_collection():
    client = chromadb.PersistentClient(path="./db_kanji")
    return client.get_or_create_collection(name="kanji_collection")