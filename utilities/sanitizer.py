import re

def clean_html(raw_html):
    """Menghapus tag HTML dan merapikan spasi."""
    if not raw_html:
        return ""
    # Hapus tag HTML
    clean = re.sub(r'<.*?>', '', raw_html)
    # Hapus entitas seperti &nbsp;
    clean = re.sub(r'&[^;]+;', ' ', clean)
    # Ubah multiple newline/spasi menjadi satu spasi saja
    clean = " ".join(clean.split())
    return clean.strip()

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