import re

def clean_html(raw_html, preserve_newline = False):
    """Menghapus tag HTML dan merapikan spasi."""

    if not raw_html: return ""

    # Ganti tag blok dengan newline jika kita ingin menjaga struktur baris
    if preserve_newline:
        raw_html = re.sub(r'</div>|</li>|</p>|</br\s*/?>', '\n', raw_html)

    # Hapus tag HTML
    clean = re.sub(r'<.*?>', '', raw_html)
    # Hapus entitas seperti &nbsp;
    clean = re.sub(r'&[^;]+;', ' ', clean)

    if preserve_newline:
        # Bersihkan spasi di tiap baris, tapi pertahankan barisnya
        lines = [line.strip() for line in clean.split('\n') if line.strip()]
        return "\n".join(lines)
    else:
        # Normalisasi spasi menjadi satu baris (untuk field tunggal)
        return " ".join(clean.split()).strip()
    
def extract_svg_filename(html_string):
    # Mencari nama file di dalam tag <img src="xxx.svg">
    match = re.search(r'src="([^"]+\.svg)"', html_string)
    return match.group(1) if match else ""

# Masukkan ke metadata:
# all_metas.append({
#    "strokes": stroke_count,
#    "stroke_file": extract_svg_filename(f.get('Stroke number', {}).get('value', ''))
# })

# penggunaan di wrapper UI untuk menampilkan gambar SVG
# import os

# ANKI_MEDIA_DIR = "C:/Users/pc/AppData/Roaming/Anki2/User 1/collection.media/"

# def get_image_path(filename):
#     # Gabungkan Base Path dengan nama file dari Metadata
#     return os.path.join(ANKI_MEDIA_DIR, filename)

# Saat AI menampilkan hasil pencarian:
# 1. Ambil metadata 'stroke_file' dari ChromaDB
# 2. Wrapper akan me-render file tersebut di UI