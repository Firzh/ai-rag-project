import db_config as db
import utilities.anki_sync as anki
from utilities.id_handler import check_id_exists, generate_kanji_id
from utilities.sanitizer import clean_html
from utilities.check_model import check_model

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
        clean_meaning = clean_html(raw_meaning)
        
        # 3. Test ID Generator
        kanji = clean_html(f.get('Kanji', {}).get('value', 'unknown'))
        generated_id = generate_kanji_id(note['noteId'], kanji)

        # 4. Display Results
        print(f"RAW HTML   : {raw_meaning[:50]}...")
        print(f"CLEAN TEXT : {clean_meaning}")
        print(f"GEN-ID     : {generated_id}")
        
        # 5. Check Duplicate
        exists = check_id_exists("japanese_learning", generated_id)
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

# def test_anki_sanitization_preview():
#     print("\n--- [TEST 2] Preview Sanitasi Data Anki (Dry Run) ---")
#     try:
#         # Ambil 1 kartu secara acak untuk preview
#         note_ids = anki.invoke("findNotes", query="rated:1")['result']
#         if not note_ids:
#             print("ℹ️ Tidak ada data latihan hari ini untuk diuji.")
#             return

#         note = anki.invoke("notesInfo", notes=[note_ids[0]])['result'][0]
        
#         print(f"ID Kartu: {note['noteId']}")
#         print("-" * 30)
#         print("RAW DATA (Sample Field 'Meanings'):")
#         print(note['fields'].get('Meanings', {}).get('value', 'KOSONG'))
        
#         print("\nCLEAN DATA (Hasil Sanitasi):")
#         print(clean_html(note['fields'].get('Meanings', {}).get('value', '')))
        
#         print("\nFINAL DOCUMENT STRUCTURE:")
#         # Menggunakan logika build_rich_doc dari anki_sync
#         print(anki.build_rich_doc(note['fields']))
#         print("-" * 30)
        
#     except Exception as e:
#         print(f"❌ Error saat uji data: {e}")

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
        elif choice == "4":anki.test_numbering()
        elif choice == "0": break
        
        input("\nTekan Enter untuk lanjut...")

if __name__ == "__main__":
    main_test()