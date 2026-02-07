import db_config as db
import utilities.anki_sync as anki
import utilities.id_handler as id_handler
import utilities.sanitizer as sanitizer

def run_anki_logic_test():
    """Uji alur sanitasi dan pembuatan ID tanpa memasukkan ke DB."""
    print("\n--- [TEST] PROSES SANITASI & ID GENERATION ---")
    try:
        # 1. Ambil sampel dari Anki
        note_ids = anki.invoke("findNotes", query="rated:1")['result']
        if not note_ids:
            print("ℹ️ Tidak ada sesi latihan Anki hari ini untuk diuji.")
            return

        note = anki.invoke("notesInfo", notes=[note_ids[0]])['result'][0]
        f = note['fields']

        # 2. Test Sanitizer
        raw_meaning = f.get('Meanings', {}).get('value', '')
        clean_meaning = sanitizer.html_cleaner(raw_meaning)
        
        # 3. Test ID Generator
        kanji = sanitizer.html_cleaner(f.get('Kanji', {}).get('value', 'unknown'))
        generated_id = id_handler.generate_kanji_id(note['noteId'], kanji)

        # 4. Display Results
        print(f"RAW HTML   : {raw_meaning[:50]}...")
        print(f"CLEAN TEXT : {clean_meaning}")
        print(f"GEN-ID     : {generated_id}")
        
        # 5. Check Duplicate
        exists = id_handler.check_id_exists("japanese_learning", generated_id)
        print(f"DUPLIKAT?  : {'🚩 YA' if exists else '✅ AMAN (Belum ada)'}")

    except Exception as e:
        print(f"❌ Error saat uji: {e}")

def test_anki_connection():
    print("\n--- [TEST 1] Cek Koneksi AnkiConnect ---")
    try:
        res = anki.invoke("version")
        print(f"✅ Terhubung! AnkiConnect Versi: {res['result']}")
    except:
        print("❌ GAGAL: Anki Desktop belum dibuka atau Add-on tidak aktif.")

def test_increment():
    print("\n--- [TEST] VERIFIKASI PENOMORAN CONTOH ---")
    
    final_doc = anki.build_rich_doc()
    print("Hasil Konstruksi Dokumen:")
    print("-" * 20)
    print(final_doc)
    print("-" * 20)
    
    if "Contoh 3:" in final_doc:
        print("✅ Berhasil: Contoh dipisah menjadi Contoh 1, 2, dan 3.")
    else:
        print("❌ Gagal: Contoh masih menyatu.")

def check_model():
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

def main_test():
    while True:
        db.clear_screen()
        print("=== CENTRAL TESTING & DEBUG CENTER ===")
        print("1. Uji Koneksi Anki")
        print("2. Uji Sanitasi & Logic ID Anki (Daily)")
        print("3. Cek Dimensi Vektor (Verify L12)")
        print("4. Cek Numbering ID Unik")
        print("0. Kembali ke Menu Utama")
        
        choice = input("\nPilih Uji: ")
        
        if choice == "1": test_anki_connection()
        elif choice == "2": run_anki_logic_test()
        elif choice == "3": check_model()
        elif choice == "4": test_increment()
        elif choice == "0": break
        
        input("\nTekan Enter untuk lanjut...")

if __name__ == "__main__":
    main_test()