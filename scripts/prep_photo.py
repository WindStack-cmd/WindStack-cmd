"""Prepare an already-background-removed portrait for ASCII conversion."""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUTPUT = ASSETS / "source-prepped.png"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def find_source() -> Path | None:
    """Choose a supplied image, ignoring generated project assets."""
    candidates = [
        path for path in ASSETS.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES and path != OUTPUT
    ]
    return candidates[0] if len(candidates) == 1 else None


def crop_to_subject(image: Image.Image) -> Image.Image:
    """Crop transparent margins while retaining a small silhouette-safe border."""
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    if not bbox:
        return image
    left, top, right, bottom = bbox
    padding = round(max(right - left, bottom - top) * 0.05)
    return image.crop((max(0, left - padding), max(0, top - padding), min(image.width, right + padding), min(image.height, bottom + padding)))


def normalize_subject(gray: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    """Improve visible detail without allowing transparent pixels to affect levels."""
    enhanced = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    visible = alpha > 16
    if not np.any(visible):
        return enhanced
    low, high = np.percentile(enhanced[visible], (2, 98))
    if high <= low:
        return enhanced
    normalized = np.clip((enhanced.astype(np.float32) - low) * 255 / (high - low), 0, 255).astype(np.uint8)
    normalized[~visible] = 255
    return normalized


def main() -> int:
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else find_source()
    if source is None or not source.is_file():
        print("No unique prepared portrait found. Add one image to assets/ or pass its path explicitly.")
        return 0
    image = crop_to_subject(Image.open(source).convert("RGBA"))
    alpha = np.asarray(image.getchannel("A"), dtype=np.uint8)
    gray = np.asarray(ImageOps.grayscale(image.convert("RGB")), dtype=np.uint8)
    prepared = Image.fromarray(normalize_subject(gray, alpha), "L")
    prepared.putalpha(Image.fromarray(alpha, "L"))
    prepared.save(OUTPUT)
    print(f"Prepared portrait from {source.name}: {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
