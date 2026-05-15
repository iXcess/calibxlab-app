#!/usr/bin/env python3
"""Regenerate favicons and logo variants from assets/calixlab-logo.png."""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SRC = ASSETS / "calixlab-logo.png"


def on_white(im: Image.Image, size: int | None = None) -> Image.Image:
    out = Image.new("RGBA", im.size, (255, 255, 255, 255))
    out.paste(im, (0, 0), im)
    if size:
        out = out.resize((size, size), Image.Resampling.LANCZOS)
    return out.convert("RGB")


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"Missing source logo: {SRC}")
    ASSETS.mkdir(parents=True, exist_ok=True)
    src = Image.open(SRC).convert("RGBA")
    w, h = src.size
    side = int(min(w, h) * 0.52)
    left = (w - side) // 2
    top = (h - side) // 2
    mark = src.crop((left, top, left + side, top + side))
    mark.save(ASSETS / "calixlab-mark.png")
    mark_rgb = on_white(mark)
    for s in (16, 32, 48, 64, 128, 180, 192, 512):
        mark_rgb.resize((s, s), Image.Resampling.LANCZOS).save(ASSETS / f"icon-{s}.png")
    mark_rgb.resize((16, 16), Image.Resampling.LANCZOS).save(ASSETS / "favicon-16.png")
    mark_rgb.resize((32, 32), Image.Resampling.LANCZOS).save(ASSETS / "favicon-32.png")
    full = on_white(src)
    full.save(ASSETS / "calixlab-logo-white-bg.jpg", quality=92)
    full.resize((400, int(400 * h / w)), Image.Resampling.LANCZOS).save(
        ASSETS / "calixlab-logo-header.png"
    )
    print("Wrote brand assets to", ASSETS)


if __name__ == "__main__":
    main()
