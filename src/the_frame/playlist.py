import logging
import random
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp"}


@dataclass
class ImageItem:
    path: Path


@dataclass
class QuoteItem:
    text: str
    author: str


def _build_deck(image_dir, quotes):
    if image_dir.is_dir():
        images = [
            ImageItem(path=p)
            for p in sorted(image_dir.iterdir())
            if p.is_file() and p.suffix.lower() in _IMAGE_SUFFIXES
        ]
    else:
        logger.warning("Image directory not found: %s", image_dir)
        images = []

    quote_items = [QuoteItem(text=q["text"], author=q["author"]) for q in quotes]
    return images + quote_items


class Playlist:
    def __init__(self, image_dir, quotes):
        self._image_dir = Path(image_dir)
        self._quotes = quotes
        self._deck = []

    def next(self):
        if not self._deck:
            self._deck = _build_deck(self._image_dir, self._quotes)
            if not self._deck:
                raise RuntimeError(
                    f"Playlist is empty: no images in '{self._image_dir}' and no quotes configured"
                )
            random.shuffle(self._deck)
        return self._deck.pop()
