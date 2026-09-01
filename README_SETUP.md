# WindStack-cmd profile art setup

This repository generates a self-contained terminal-style GitHub profile. SVG assets use only embedded SVG/CSS animation—no JavaScript, third-party statistics service, or token is required.

## Structure

- `scripts/` contains the generators and checks.
- `data/contributions.json` caches public contribution data.
- `assets/` contains generated README assets. A portrait source is intentionally absent.
- `.github/workflows/update-profile-art.yml` refreshes only the contribution assets daily.

## First use

Use Python 3.11+ and optionally create an environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r scripts/requirements.txt
python scripts/make_info_card.py
python scripts/make_ascii_svg.py
python scripts/fetch_contributions.py
python scripts/render_heatmap_svg.py
python scripts/test_profile_art.py
```

`requirements.txt` contains only `requests` and `beautifulsoup4`. The optional, heavier portrait tools are deliberately isolated in `requirements-local.txt`; install them only when you decide to process a photo.

## Later: add a portrait

Put a photo at `assets/source-photo.jpg`, then explicitly install the local requirements and run:

```powershell
pip install -r scripts/requirements-local.txt
python scripts/prep_photo.py assets/source-photo.jpg
python scripts/make_ascii_svg.py
```

`prep_photo.py` reports a clear message if the photo or optional dependencies are missing. It uses rembg, OpenCV, Pillow, and NumPy only in this later local step—never in Actions. In PowerShell, a static card is generated with `$env:STATIC=1; python scripts/make_info_card.py; Remove-Item Env:STATIC`.

## Customize

Edit the `PROFILE` dictionary near the top of `scripts/make_info_card.py`, then run `python scripts/make_info_card.py`. Use `STATIC=1 python scripts/make_info_card.py` for a non-animated card. Edit README placeholder sections, colors (`PALETTE` and SVG style blocks), or animation delays in the generators as desired.

## Automation

The GitHub Action runs daily and manually on demand. It installs only `scripts/requirements.txt`, fetches the public calendar without credentials, regenerates the heatmap, and commits changed graph files. It does not process portraits. If GitHub changes its calendar HTML or a network request fails, the job stops instead of fabricating data.
