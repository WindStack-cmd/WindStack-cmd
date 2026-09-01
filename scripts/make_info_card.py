"""Generate the self-contained terminal-style profile card."""
from __future__ import annotations

import os
import textwrap
from pathlib import Path

PROFILE = [
    ("USER", "Pratik Yadav"),
    ("ROLE", "Aspiring Data Scientist"),
    ("FOCUS", "AI / ML / Data Science"),
    ("LEARNING", "DSA / LLMs / RAG / AI"),
    ("LANGUAGES", "Python / SQL / JavaScript"),
    ("STACK", "Flask / React / Node.js"),
    ("DATABASES", "MongoDB / MySQL / SQLite"),
    ("PROJECTS", "GitIntel / FireGuard AI / Student Helper / KARN"),
    ("BUILDING", "Building intelligent systems at the intersection of data, AI and software."),
    ("STATUS", "Turning data, ideas and code into intelligent systems. 🚀"),
]

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "info-card.svg"


def escape_xml(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> None:
    static = os.getenv("STATIC") == "1"
    rows, y, line_number = [], 92, 0

    for label, value in PROFILE:
        for index, line in enumerate(textwrap.wrap(value, width=42, break_long_words=False)):
            delay = "" if static else f' style="animation-delay:{.18 + line_number * .09:.2f}s"'
            if index == 0:
                rows.append(
                    f'<text x="28" y="{y}" class="line"{delay}>'
                    f'<tspan class="key">{label:<11}</tspan><tspan> : {escape_xml(line)}</tspan></text>'
                )
            else:
                rows.append(f'<text x="134" y="{y}" class="line"{delay}>{escape_xml(line)}</text>')
            y += 24
            line_number += 1

    css = (
        '.line{font:13px monospace;fill:#c9d1d9}.key{fill:#58a6ff}'
        if static
        else '.line{font:13px monospace;fill:#c9d1d9;opacity:0;animation:enter .35s ease-out forwards}.key{fill:#58a6ff}@keyframes enter{from{opacity:0;transform:translateX(-7px)}to{opacity:1;transform:translateX(0)}}'
    )
    height = y + 26
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="500" height="{height}" viewBox="0 0 500 {height}" role="img" aria-label="Pratik Yadav profile information"><rect width="500" height="{height}" rx="12" fill="#0d1117" stroke="#30363d"/><style>{css}</style><text x="28" y="40" style="font:bold 16px monospace;fill:#7ee787">pratik@WindStack-cmd:~$ neofetch</text><text x="28" y="66" style="font:12px monospace;fill:#8b949e">----------- profile information -----------</text>{''.join(rows)}</svg>'''
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
