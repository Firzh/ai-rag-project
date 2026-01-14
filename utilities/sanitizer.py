import re

def clean_html(raw_html):
    """Menghapus tag HTML dan merapikan spasi."""
    if not raw_html:
        return ""
    # Menghapus tag HTML (apapun di dalam < >)
    clean_text = re.sub(r'<.*?>', '', raw_html)
    # Mengubah entitas HTML seperti &nbsp; menjadi spasi biasa
    clean_text = re.sub(r'&nbsp;', ' ', clean_text)
    # Menghapus spasi berlebih
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    return clean_text