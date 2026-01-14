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