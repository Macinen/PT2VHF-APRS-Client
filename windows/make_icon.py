"""Ícone Windows APRS multirresolução, otimizado para desktop, taskbar e tray.

Mantém a paleta e o símbolo de antena do PT2VHF, mas amplia a área útil
e desenha a palavra APRS individualmente por tamanho — não apenas escala
uma imagem detalhada para 16 pixels.
"""
from __future__ import annotations

from pathlib import Path
from io import BytesIO
import struct

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "windows" / "aprs_taskbar_icon.png"
OUTPUT = ROOT / "windows" / "app_icon.ico"
SIZES = (16, 24, 32, 48, 64, 128, 256)
NAVY = (13, 32, 47, 255)
CYAN = (98, 208, 243, 255)
YELLOW = (247, 194, 62, 255)
WHITE = (255, 255, 255, 255)


def _font(pixel_size: int) -> ImageFont.ImageFont:
    candidates = (
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "DejaVuSans-Bold.ttf",
    )
    for path in candidates:
        try:
            return ImageFont.truetype(path, pixel_size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_icon(size: int) -> Image.Image:
    if size not in SIZES:
        raise ValueError("Unsupported Windows icon size: {}".format(size))
    scale = 8 if size <= 32 else 4
    n = size * scale
    image = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    margin = max(1, int(n * 0.028))
    draw.rounded_rectangle(
        (margin, margin, n - margin - 1, n - margin - 1),
        radius=int(n * 0.19), fill=NAVY,
        outline=CYAN, width=max(1, int(n * 0.027)),
    )

    if size >= 24:
        draw.arc(
            (int(n*.23), int(n*.045), int(n*.77), int(n*.585)),
            205, 335, fill=CYAN, width=max(2, int(n*.045)),
        )
        draw.arc(
            (int(n*.32), int(n*.15), int(n*.68), int(n*.51)),
            205, 335, fill=CYAN, width=max(2, int(n*.043)),
        )
        draw.ellipse(
            (int(n*.452), int(n*.34), int(n*.548), int(n*.436)),
            fill=YELLOW,
        )
        draw.rounded_rectangle(
            (int(n*.478), int(n*.415), int(n*.522), int(n*.59)),
            radius=max(1, int(n*.02)), fill=YELLOW,
        )
        baseline = int(n*.61)
    else:
        baseline = int(n*.38)

    # APRS is intentionally the dominant high-contrast lettering. At 16 px,
    # drop the antenna ornament and use the full available icon for the word.
    text = "APRS"
    maximum_width = int(n * .90)
    maximum_height = int(n * (.43 if size == 16 else .29))
    font_px = int(n * (.47 if size == 16 else .33))
    font = _font(font_px)
    for candidate in range(font_px, max(2, int(n*.12)), -1):
        font = _font(candidate)
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        if right-left <= maximum_width and bottom-top <= maximum_height:
            break
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    x = (n-(right-left))/2 - left
    y = baseline + (n-baseline-(bottom-top))/2 - top
    draw.text((int(x), int(y)), text, font=font, fill=WHITE,
              stroke_width=max(0, int(n*.004)), stroke_fill=NAVY)
    return image.resize((size, size), Image.Resampling.LANCZOS)


def main() -> None:
    # The pre-existing APRS brand asset stays in the repository as reference.
    with Image.open(SOURCE) as brand:
        brand.verify()
    frames = [render_icon(size) for size in SIZES]
    # Build genuine separate PNG-backed icon images in an ICO directory.
    # Pillow's save(sizes=...) merely scales one original; hand-assembling
    # PNG frames preserves separate typography at the small Windows sizes.
    encoded = []
    for frame in frames:
        buffer = BytesIO()
        frame.save(buffer, format="PNG", optimize=True)
        encoded.append(buffer.getvalue())
    offset = 6 + len(SIZES) * 16
    entries = []
    for size, raw in zip(SIZES, encoded):
        dimension = 0 if size == 256 else size
        entries.append(struct.pack(
            "<BBBBHHII", dimension, dimension, 0, 0,
            1, 32, len(raw), offset
        ))
        offset += len(raw)
    OUTPUT.write_bytes(
        struct.pack("<HHH", 0, 1, len(SIZES)) +
        b"".join(entries) + b"".join(encoded)
    )
    print(OUTPUT)


if __name__ == "__main__":
    main()
