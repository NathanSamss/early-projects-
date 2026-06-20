"""make_icons.py — generates simple placeholder icons. Run once: python make_icons.py"""
import os
try:
    from PIL import Image, ImageDraw
except ImportError:
    raise SystemExit("Pillow not installed. Run: pip install Pillow")

os.makedirs("icons", exist_ok=True)
for size in (16, 48, 128):
    img = Image.new("RGB", (size, size), (29, 78, 216))  # blue
    d = ImageDraw.Draw(img)
    # simple shield-ish white square in the middle
    pad = size // 4
    d.rectangle([pad, pad, size - pad, size - pad], fill=(255, 255, 255))
    img.save(f"icons/icon{size}.png")
print("Icons written to icons/")
