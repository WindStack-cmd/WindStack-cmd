"""Render contribution data as a standalone, one-shot animated SVG."""
from __future__ import annotations
import json
from datetime import date, timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; INPUT=ROOT/"data/contributions.json"; OUTPUT=ROOT/"assets/contrib-heatmap.svg"
PALETTE=["#161b22","#0e4429","#006d32","#26a641","#39d353"]
def placeholder(message):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="860" height="220" viewBox="0 0 860 220" role="img" aria-label="Contribution heatmap placeholder"><rect width="860" height="220" rx="12" fill="#0d1117" stroke="#30363d"/><text x="32" y="80" style="font:bold 18px monospace;fill:#58a6ff">CONTRIBUTION HEATMAP</text><text x="32" y="120" style="font:14px monospace;fill:#c9d1d9">{message}</text><text x="32" y="155" style="font:13px monospace;fill:#8b949e">Run: python scripts/fetch_contributions.py</text></svg>'''
def main():
    OUTPUT.parent.mkdir(exist_ok=True)
    if not INPUT.is_file(): OUTPUT.write_text(placeholder("Data unavailable — no statistics shown."),encoding="utf-8"); print("No contribution JSON; wrote labeled placeholder."); return
    try: data=json.loads(INPUT.read_text(encoding="utf-8")); days=data["days"]; stats=data["statistics"]
    except (json.JSONDecodeError,KeyError,TypeError) as error: OUTPUT.write_text(placeholder("Data unavailable — invalid contribution file."),encoding="utf-8"); print(f"Invalid JSON ({error}); wrote placeholder."); return
    by_date={item["date"]:item for item in days}; end=max(date.fromisoformat(x) for x in by_date); start=end-timedelta(days=370); start-=timedelta(days=(start.weekday()+1)%7)
    cells=[]
    for offset in range(371):
        day=start+timedelta(days=offset); item=by_date.get(day.isoformat(),{"level":0}); week=offset//7; row=(day.weekday()+1)%7; delay=(week+row)*.018
        cells.append(f'<rect x="{58+week*14}" y="{42+row*14}" width="10" height="10" rx="2" fill="{PALETTE[int(item.get("level",0))]}" class="cell" style="animation-delay:{delay:.3f}s"/>')
    best=stats.get("best_day",{}); footer=f'{stats.get("total_contributions",0)} contributions · {stats.get("current_streak",0)} day current streak · best: {best.get("count",0)} on {best.get("date","—")}'
    legend=''.join(f'<rect x="{650+i*16}" y="165" width="11" height="11" rx="2" fill="{color}"/>' for i,color in enumerate(PALETTE))
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="860" height="220" viewBox="0 0 860 220" role="img" aria-label="GitHub contribution heatmap"><rect width="860" height="220" rx="12" fill="#0d1117" stroke="#30363d"/><style>.cell{{opacity:0;animation:cell .25s ease-out forwards}}@keyframes cell{{from{{opacity:0;transform:translate(-3px,-3px)}}to{{opacity:1;transform:translate(0,0)}}}}.label{{font:12px monospace;fill:#8b949e}}.footer{{font:12px monospace;fill:#c9d1d9}}</style><text x="24" y="30" style="font:bold 15px monospace;fill:#c9d1d9">Contribution activity</text><text x="24" y="54" class="label">Sun</text><text x="24" y="96" class="label">Wed</text><text x="24" y="138" class="label">Sat</text>{''.join(cells)}<text x="600" y="175" class="label">Less</text>{legend}<text x="736" y="175" class="label">More</text><text x="24" y="202" class="footer">{footer}</text></svg>'''
    OUTPUT.write_text(svg,encoding="utf-8"); print(f"Wrote {OUTPUT}")
if __name__ == "__main__": main()
