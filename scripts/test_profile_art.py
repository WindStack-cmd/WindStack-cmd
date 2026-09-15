"""Lightweight integrity checks for generated profile assets."""
from __future__ import annotations
import hashlib
import json, sys
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from fetch_contributions import parse_contribution_cell
def fail(message): print(f"FAIL: {message}"); return 1
def test_contribution_cell_parser():
    examples = [
        ('<td data-date="2026-01-01" data-level="0" aria-label="No contributions on Jan 1, 2026"></td>', 0, 0),
        ('<td data-date="2026-01-02" data-level="1" title="1 contribution on Jan 2, 2026"></td>', 1, 1),
        ('<td data-date="2026-01-03" data-level="4" aria-label="123 contributions on Jan 3, 2026"></td>', 123, 4),
        ('<td id="day-four" data-date="2026-01-04" data-level="2"></td><tool-tip for="day-four">12 contributions on Jan 4, 2026</tool-tip>', 12, 2),
    ]
    for markup, expected_count, expected_level in examples:
        cell = BeautifulSoup(markup, "html.parser").select_one("[data-date]")
        parsed = parse_contribution_cell(cell)
        assert parsed and parsed["count"] == expected_count and parsed["level"] == expected_level
def main():
    try: import requests, bs4
    except ImportError as error: return fail(f"Required contribution dependency unavailable: {error}")
    try: test_contribution_cell_parser()
    except AssertionError: return fail("Contribution-cell parser did not read representative accessible count text")
    readme=(ROOT/"README.md").read_text(encoding="utf-8")
    if any(marker in readme for marker in ("<<<<<<<", "=======", ">>>>>>>")):
        return fail("README contains merge conflict markers")
    whoami_marker="pratik@github ~ $ whoami"
    contributions_marker="pratik@github ~ $ ./contributions.sh"
    if readme.count(whoami_marker) != 1 or readme.count(contributions_marker) != 1:
        return fail("README must contain exactly one whoami and contributions section")
    if readme.index(whoami_marker) > readme.index(contributions_marker):
        return fail("README whoami section must appear before contributions section")
    for path in ("assets/contrib-heatmap.svg","assets/windstack-ascii.svg","assets/info-card.svg"):
        asset=ROOT/path
        if not asset.is_file(): return fail(f"Missing {path}")
        text=asset.read_text(encoding="utf-8")
        try: ET.fromstring(text)
        except ET.ParseError as error: return fail(f"Invalid SVG {path}: {error}")
        external = text.replace('xmlns="http://www.w3.org/2000/svg"', "")
        if "<script" in text.lower() or "http://" in external or "https://" in external: return fail(f"Unsafe external/script dependency in {path}")
        if path not in readme: return fail(f"README does not reference {path}")
    heatmap_key=hashlib.sha256((ROOT/"assets/contrib-heatmap.svg").read_bytes()).hexdigest()[:12]
    heatmap_references=re.findall(r'src="(\./assets/contrib-heatmap\.svg(?:\?v=[^"]*)?)"', readme)
    if len(heatmap_references) != 1:
        return fail("README must contain exactly one heatmap image reference")
    if heatmap_references[0] != f"./assets/contrib-heatmap.svg?v={heatmap_key}":
        return fail("README heatmap reference does not match the generated SVG cache key")
    contribution=ROOT/"data/contributions.json"
    if contribution.is_file():
        try:
            payload=json.loads(contribution.read_text(encoding="utf-8"))
            assert isinstance(payload["days"],list)
            assert all({"date","count","level"} <= set(day) for day in payload["days"])
            total=payload["statistics"]["total_contributions"]
            assert f"{total} contributions" in (ROOT/"assets/contrib-heatmap.svg").read_text(encoding="utf-8")
        except (json.JSONDecodeError,KeyError,AssertionError) as error: return fail(f"Invalid contributions JSON: {error}")
    print("PASS: profile-art assets and references are valid."); return 0
if __name__ == "__main__": raise SystemExit(main())
