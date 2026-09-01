"""Generate a self-contained, one-shot animated ASCII portrait SVG."""
from __future__ import annotations

import html
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "source-prepped.png"
OUTPUT = ROOT / "assets" / "windstack-ascii.svg"
RAMP = " .`:-=+*cs#%@"
COLS = 66


def svg_placeholder() -> str:
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="360" height="300" viewBox="0 0 360 300" role="img" aria-label="Portrait placeholder"><rect width="360" height="300" rx="12" fill="#0d1117" stroke="#30363d"/><style>.t{font:14px monospace;fill:#8b949e}.a{fill:#58a6ff;font-weight:bold}</style><text x="28" y="45" class="a">WindStack-cmd@github:~$ portrait</text><text x="88" y="145" class="t">PHOTO PLACEHOLDER</text></svg>'''


def main() -> None:
    OUTPUT.parent.mkdir(exist_ok=True)
    if not SOURCE.is_file():
        OUTPUT.write_text(svg_placeholder(), encoding="utf-8")
        print(f"No prepared photo; wrote placeholder: {OUTPUT}")
        return

    image = Image.open(SOURCE).convert("LA")
    rows = max(26, min(50, round(image.height / image.width * COLS * 0.5)))
    image = image.resize((COLS, rows), Image.Resampling.LANCZOS)
    luminance, alpha = image.split()
    lines = []
    for y in range(rows):
        characters = []
        for x in range(COLS):
            if alpha.getpixel((x, y)) < 48:
                characters.append(" ")
            else:
                shade = luminance.getpixel((x, y))
                characters.append(RAMP[shade * (len(RAMP) - 1) // 255])
        lines.append(
            f'<text x="18" y="{38 + y * 10}" class="row" style="animation-delay:{y * .055:.3f}s">'
            f'{html.escape("".join(characters))}</text>'
        )

    height = 56 + rows * 10
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="360" height="{height}" viewBox="0 0 360 {height}" role="img" aria-label="ASCII portrait of Pratik Yadav"><rect width="360" height="{height}" rx="12" fill="#0d1117" stroke="#30363d"/><style>.title{{font:12px monospace;fill:#58a6ff}}.row{{font:9px monospace;fill:#c9d1d9;white-space:pre;opacity:0;animation:reveal .3s ease-out forwards}}@keyframes reveal{{from{{opacity:0;transform:translateX(-8px)}}to{{opacity:1;transform:translateX(0)}}}}</style><text x="18" y="22" class="title">pratik@WindStack-cmd:~$ portrait</text>{''.join(lines)}</svg>'''
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Wrote ASCII portrait: {OUTPUT}")


if __name__ == "__main__":
    main()
