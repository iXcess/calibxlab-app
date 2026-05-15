#!/usr/bin/env python3
"""Regenerate favicons and logo variants from assets/calixlab-logo.png (or .jpg)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SRC_CANDIDATES = (ASSETS / "calixlab-logo.png", ASSETS / "calixlab-logo.jpg")


def find_source() -> Path:
    for p in SRC_CANDIDATES:
        if p.exists():
            return p
    raise SystemExit(f"Missing source logo in {ASSETS} (calixlab-logo.png or .jpg)")


def remove_near_white_bg(im: Image.Image, threshold: int = 238, softness: int = 18) -> Image.Image:
    """Make white / off-white pixels transparent with soft edges."""
    rgba = im.convert("RGBA")
    px = rgba.load()
    w, h = rgba.size
    lo = threshold - softness
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            # Treat high, low-saturation pixels as background.
            mx, mn = max(r, g, b), min(r, g, b)
            if mx < lo:
                continue
            if mx >= threshold and (mx - mn) <= 28:
                px[x, y] = (r, g, b, 0)
            elif mx >= lo and (mx - mn) <= 32:
                t = (mx - lo) / max(softness, 1)
                px[x, y] = (r, g, b, int(a * (1.0 - min(1.0, t))))
    return rgba


def trim_transparent(im: Image.Image, pad: int = 8) -> Image.Image:
    bbox = im.getbbox()
    if not bbox:
        return im
    x0, y0, x1, y1 = bbox
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(im.size[0], x1 + pad)
    y1 = min(im.size[1], y1 + pad)
    return im.crop((x0, y0, x1, y1))


def save_png(im: Image.Image, path: Path) -> None:
    im.save(path, format="PNG", optimize=True)


def save_icons(mark: Image.Image) -> None:
    for s in (16, 32, 48, 64, 128, 180, 192, 512):
        save_png(mark.resize((s, s), Image.Resampling.LANCZOS), ASSETS / f"icon-{s}.png")
    save_png(mark.resize((16, 16), Image.Resampling.LANCZOS), ASSETS / "favicon-16.png")
    save_png(mark.resize((32, 32), Image.Resampling.LANCZOS), ASSETS / "favicon-32.png")
    mark.resize((32, 32), Image.Resampling.LANCZOS).save(
        ASSETS / "favicon.ico",
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
    )


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    src_path = find_source()
    raw = Image.open(src_path)
    logo = trim_transparent(remove_near_white_bg(raw))
    save_png(logo, ASSETS / "calixlab-logo.png")

    w, h = logo.size
    side = int(min(w, h) * 0.52)
    left = (w - side) // 2
    top = (h - side) // 2
    mark = trim_transparent(remove_near_white_bg(logo.crop((left, top, left + side, top + side))))
    save_png(mark, ASSETS / "calixlab-mark.png")
    save_icons(mark)

    header_w = 400
    header_h = max(1, int(header_w * h / w))
    header = logo.resize((header_w, header_h), Image.Resampling.LANCZOS)
    save_png(header, ASSETS / "calixlab-logo-header.png")

    # Optional flat export for print / legacy
    flat = Image.new("RGB", logo.size, (255, 255, 255))
    flat.paste(logo, mask=logo.split()[3])
    flat.save(ASSETS / "calixlab-logo-white-bg.jpg", quality=92)

    print("Wrote transparent brand assets to", ASSETS)


if __name__ == "__main__":
    main()
