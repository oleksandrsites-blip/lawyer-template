#!/usr/bin/env python3
"""Готує фото адвоката для шаблону: вирізає фон, робить ч/б, зберігає WebP.

    python3 tools/photo.py ivanenko ~/Desktop/ivanenko.jpg
    -> public/img/leads/ivanenko/cut-700.webp і cut-1100.webp
    -> у leads/ivanenko.json: "photo": "/img/leads/ivanenko/cut"

Потрібні: macOS 14+ (Vision) і Pillow (pip3 install pillow).
Найкраще працює портрет до пояса на однотонному фоні.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parent.parent


def main(slug, src):
    out_dir = ROOT / "public" / "img" / "leads" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        cut = Path(tmp) / "cut.png"
        subprocess.run(["swift", str(ROOT / "tools" / "cutout.swift"), str(src), str(cut)], check=True)
        im = Image.open(cut).convert("RGBA")

    alpha = im.getchannel("A")
    box = alpha.point(lambda a: 255 if a > 20 else 0).getbbox()
    im = im.crop((box[0], box[1], box[2], im.height))  # низ не обрізаємо: людина «стоїть» на краю картки
    gray = ImageOps.grayscale(im.convert("RGB"))
    gray = ImageEnhance.Contrast(gray).enhance(1.18)
    gray = ImageEnhance.Brightness(gray).enhance(1.03)
    bw = Image.merge("RGBA", (gray, gray, gray, im.getchannel("A")))

    for w in (700, 1100):
        r = bw.resize((w, round(bw.height * w / bw.width)), Image.LANCZOS)
        r.save(out_dir / f"cut-{w}.webp", "WEBP", quality=80, method=6)
        print(f"✓ {(out_dir / f'cut-{w}.webp').relative_to(ROOT)}  {r.size[0]}×{r.size[1]}")
    print(f'У leads/{slug}.json: "photo": "/img/leads/{slug}/cut"')


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], Path(sys.argv[2]).expanduser())
