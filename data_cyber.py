# data_cyber.py

DATA_LIST = [
    {
        "id": "cyber_sqli",
        "doc": "SQL Injection (SQLi) adalah teknik serangan di mana penyerang memasukkan perintah SQL berbahaya ke dalam input form untuk memanipulasi database. Pencegahan: Gunakan Prepared Statements atau Parameterized Queries.",
        "meta": {"category": "web_security", "priority": "high"}
    },
    {
        "id": "cyber_phishing",
        "doc": "Phishing adalah upaya penipuan untuk mendapatkan informasi sensitif seperti password dan kartu kredit dengan menyamar sebagai entitas tepercaya dalam komunikasi elektronik (email/WA). Ciri: URL yang sedikit berbeda (misal: g00gle.com).",
        "meta": {"category": "social_engineering", "priority": "high"}
    },
    {
        "id": "cyber_bruteforce",
        "doc": "Brute Force Attack adalah metode serangan dengan mencoba semua kemungkinan kombinasi password secara otomatis hingga berhasil. Pencegahan: Implementasi Rate Limiting, Account Lockout, dan penggunaan MFA (Multi-Factor Authentication).",
        "meta": {"category": "network_security", "priority": "medium"}
    },
    {
        "id": "cyber_xss",
        "doc": "Cross-Site Scripting (XSS) terjadi ketika penyerang menyisipkan script berbahaya (biasanya JavaScript) ke halaman web yang dilihat pengguna lain. Pencegahan: Melakukan sanitasi input dan output encoding.",
        "meta": {"category": "web_security", "priority": "high"}
    }
]