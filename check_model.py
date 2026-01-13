import db_config as db

# Ambil koleksi
collection = db.get_collection("japanese_learning")

# Akses internal embedding function
ef = collection._embedding_function

# Cek nama model yang terdaftar di dalam objek SentenceTransformer
if hasattr(ef, 'models'): # Jika menggunakan SentenceTransformerEmbeddingFunction
    # Biasanya model tersimpan di urutan pertama dalam list modules
    model_name = ef.model_name
    print(f"--- Verifikasi Engine ---")
    print(f"Model Name Terdeteksi: {model_name}")
    
    if "L12" in model_name:
        print("✅ KONFIRMASI: Sistem menggunakan versi 12-Layer (Multilingual).")
    else:
        print("⚠️ PERINGATAN: Sistem terdeteksi menggunakan model lain.")