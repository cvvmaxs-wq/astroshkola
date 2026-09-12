import base64, io, re, sys
from PIL import Image, ImageOps

ROOT = r"E:\astroo"
SRC = ROOT + r"\src"

def jpg_b64(path, width, quality=82, crop=None):
    im = Image.open(path)
    im = ImageOps.exif_transpose(im).convert("RGB")
    if crop:  # crop to aspect ratio (w:h) around center-top
        aw, ah = crop
        W, H = im.size
        target = W * ah / aw
        if target < H:
            top = int((H - target) * 0.12)
            im = im.crop((0, top, W, int(top + target)))
    if im.width > width:
        im = im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    data = buf.getvalue()
    print(f"{path.split(chr(92))[-1]}: {im.size} {len(data)//1024} KB")
    return "data:image/jpeg;base64," + base64.b64encode(data).decode()

html = open(SRC + r"\template.html", encoding="utf-8").read()
html = html.replace("{{IMG_AUTHOR}}", jpg_b64(r"C:\Users\Mello\Downloads\Telegram Desktop\IMG_7947.jpg", 1000, 80, crop=(4, 5)))
html = html.replace("{{IMG_COVER}}",  jpg_b64(SRC + r"\pdf_p1.jpg", 700, 82))
html = html.replace("{{IMG_TOC}}",    jpg_b64(SRC + r"\pdf_p3.jpg", 700, 80))
assert "{{" not in html, "unreplaced placeholder"
open(ROOT + r"\index.html", "w", encoding="utf-8").write(html)
print("index.html:", len(html.encode())//1024, "KB")

# --- версия для Artifact (claude.ai): без <html>/<head>/<body>-обвязки и <meta>, короткий <title>
import os
art = html
art = re.sub(r"<!DOCTYPE html>\s*<html[^>]*>\s*<head>\s*", "", art)
art = re.sub(r"\s*</head>\s*<body>\s*", "\n", art)
art = re.sub(r"\s*</body>\s*</html>\s*$", "\n", art)
art = re.sub(r"<meta[^>]*>\s*", "", art)
art = re.sub(r"<title>.*?</title>", "<title>ASTROшкола</title>", art, count=1)
art_dir = os.environ.get("ARTIFACT_DIR", SRC)
open(os.path.join(art_dir, "astroshkola-artifact.html"), "w", encoding="utf-8").write(art)
print("artifact:", os.path.join(art_dir, "astroshkola-artifact.html"))
