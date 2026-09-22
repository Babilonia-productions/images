#!/usr/bin/env python3
"""Generate 1200x630 Open Graph preview images.

Link previews on WhatsApp, Slack, iMessage, LinkedIn and X all want a
landscape image around 1200x630. Our campaign stills are mostly portrait and
some run past 1MB, which WhatsApp in particular quietly refuses to render.
This script crops a chosen still per page down to a consistent 1200x630 card
and keeps it under MAX_KB so every platform renders it.

Run from the repo root after adding a campaign:

    python3 tools/generate-og-images.py

Add an entry to CARDS below for each new page. `focal_y` is where the crop
window sits vertically: 0.0 keeps the top of the frame, 1.0 the bottom, and
0.5 centres it. Portraits usually want ~0.35 so faces survive the crop.
"""

import os
import sys

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow is required:  python3 -m pip install Pillow")

OUT_DIR = "assets/img/og"
WIDTH, HEIGHT = 1200, 630
MAX_KB = 300

# name -> (source image, focal_y)
CARDS = {
    # Case studies
    "prostandard-flamengo": ("assets/img/prostandard-01.jpg", 0.45),
    "magali-pascal": ("assets/img/magali-pascal-05.jpg", 0.00),
    "floyd": ("assets/img/floyd-03.jpg", 0.10),
    "nike-nocta": ("assets/img/nike-nocta-02.png", 0.18),
    "soli-sun": ("assets/img/soli-sun-02.jpg", 0.05),
    "ernest-leoty": ("assets/img/ERNEST LEOTY-98.jpg", 0.20),
    "casa-rosa": ("assets/img/CASA ROSA-7.jpg", 0.42),
    "coolway": ("assets/img/COOLWAY-19.jpg", 0.38),
    "dsquared2": ("assets/img/dsquared2-02.jpg", 0.00),
    # Site-level cards
    "default": ("assets/img/magali-pascal-05.jpg", 0.00),
    "work": ("assets/img/prostandard-01.jpg", 0.45),
    "blog": ("assets/img/floyd-03.jpg", 0.10),
    # Blog posts
    "post-brazil-moment": ("assets/img/magali-pascal-05.jpg", 0.00),
    "post-ss2027": ("assets/img/prostandard-03.jpg", 0.45),
    "post-favela": ("assets/img/dsquared2-04.jpg", 0.00),
    "post-storytelling": ("assets/img/ERNEST LEOTY-98.jpg", 0.20),
}


def build(name, source, focal_y):
    if not os.path.exists(source):
        print(f"  !! missing source: {source}")
        return False

    img = Image.open(source)
    img = ImageOps.exif_transpose(img)
    if img.mode != "RGB":
        img = img.convert("RGB")

    src_w, src_h = img.size
    target_ratio = WIDTH / HEIGHT

    # Take the largest window of the right aspect ratio, then place it
    # vertically (or horizontally) according to the focal point.
    if src_w / src_h > target_ratio:
        crop_h = src_h
        crop_w = round(src_h * target_ratio)
        left = round((src_w - crop_w) / 2)
        top = 0
    else:
        crop_w = src_w
        crop_h = round(src_w / target_ratio)
        left = 0
        top = round((src_h - crop_h) * focal_y)

    card = img.crop((left, top, left + crop_w, top + crop_h))
    card = card.resize((WIDTH, HEIGHT), Image.LANCZOS)

    out = os.path.join(OUT_DIR, f"{name}.jpg")
    for quality in (88, 84, 80, 76, 72, 68):
        card.save(out, "JPEG", quality=quality, optimize=True, progressive=True)
        kb = os.path.getsize(out) / 1024
        if kb <= MAX_KB:
            break

    upscaled = " (upscaled)" if crop_w < WIDTH else ""
    print(f"  {name:24} {kb:5.0f}KB  q{quality}  <- {source}{upscaled}")
    return True


def main():
    if not os.path.isdir("assets/img"):
        sys.exit("Run this from the repository root.")
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Writing {WIDTH}x{HEIGHT} cards to {OUT_DIR}/")
    ok = sum(build(n, s, f) for n, (s, f) in sorted(CARDS.items()))
    print(f"Done: {ok}/{len(CARDS)} cards.")


if __name__ == "__main__":
    main()
