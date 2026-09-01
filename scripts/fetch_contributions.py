"""Fetch public GitHub contribution data without API credentials."""
from __future__ import annotations
import json, re
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]; URL="https://github.com/users/WindStack-cmd/contributions"; OUTPUT=ROOT/"data/contributions.json"
COUNT_PATTERN = re.compile(r"\b(\d[\d,]*)\s+contributions?\b", re.IGNORECASE)

def accessible_cell_text(node):
    """Return contribution wording exposed by the cell or its semantic tooltip."""
    texts = []
    for element in [node, *node.find_all(True)]:
        for attribute in ("aria-label", "title"):
            if value := element.get(attribute):
                texts.append(value)
    if text := node.get_text(" ", strip=True):
        texts.append(text)

    # GitHub may place a <tool-tip for="cell-id"> beside, rather than inside, a cell.
    cell_id = node.get("id")
    if cell_id:
        container = node.find_parent()
        if container:
            for tooltip in container.find_all(attrs={"for": cell_id}):
                texts.extend(filter(None, (tooltip.get("aria-label"), tooltip.get("title"), tooltip.get_text(" ", strip=True))))
    return " ".join(texts)

def parse_contribution_cell(node):
    """Parse one calendar cell without assuming GitHub provides data-count."""
    day = node.get("data-date")
    level = node.get("data-level")
    if not day or level is None or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
        return None
    try:
        level = max(0, min(4, int(level)))
    except ValueError:
        return None

    wording = accessible_cell_text(node)
    match = COUNT_PATTERN.search(wording)
    if match:
        count = int(match.group(1).replace(",", ""))
    elif "no contributions" in wording.lower():
        count = 0
    else:
        # Retain compatibility with older markup, but never default a missing count to zero.
        raw_count = node.get("data-count")
        if raw_count is None:
            return None
        try:
            count = int(raw_count)
        except ValueError:
            return None
    return {"date": day, "count": count, "level": level}
def streaks(days):
    current=longest=run=0
    for d in days:
        run=run+1 if d["count"]>0 else 0; longest=max(longest,run)
    for d in reversed(days):
        if d["count"]>0: current+=1
        else: break
    return current,longest
def main():
    try: response=requests.get(URL,headers={"User-Agent":"WindStack-profile-art/1.0","Accept":"text/html"},timeout=30); response.raise_for_status()
    except requests.RequestException as error: raise SystemExit(f"Could not fetch public contributions: {error}")
    soup=BeautifulSoup(response.text,"html.parser"); cells=[]
    for node in soup.select("[data-date]"):
        if cell := parse_contribution_cell(node):
            cells.append(cell)
    cells=sorted({item["date"]:item for item in cells}.values(),key=lambda item:item["date"])[-371:]
    if len(cells)<200: raise SystemExit("GitHub contribution cells were not found in the expected public calendar format; no data was written.")
    monthly=defaultdict(int)
    for item in cells: monthly[item["date"][:7]]+=item["count"]
    current,longest=streaks(cells); best=max(cells,key=lambda item:item["count"])
    payload={"username":"WindStack-cmd","fetched_at":datetime.now().astimezone().isoformat(),"days":cells,"statistics":{"total_contributions":sum(x["count"] for x in cells),"current_streak":current,"longest_streak":longest,"best_day":best,"monthly_totals":dict(monthly)}}
    OUTPUT.parent.mkdir(exist_ok=True); OUTPUT.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8"); print(f"Fetched {len(cells)} days to {OUTPUT}")
if __name__ == "__main__": main()
