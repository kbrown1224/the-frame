import logging
import time
import tomllib
from pathlib import Path

from PIL import Image

from the_frame.playlist import ImageItem, Playlist
from the_frame.quote_renderer import render_quote
from the_frame.waveshare_epd.screen import Screen

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)


def _load_toml(path):
    with open(path, "rb") as f:
        return tomllib.load(f)


def main():
    config = _load_toml(Path("config.toml"))
    quotes_data = _load_toml(Path(config.get("quotes_file", "quotes.toml")))

    playlist = Playlist(
        image_dir=Path(config.get("image_dir", "images")),
        quotes=quotes_data.get("quotes", []),
    )
    interval = config.get("interval_seconds", 300)

    screen = Screen()
    screen.init()
    logger.info("Display ready — interval %ds", interval)

    try:
        while True:
            item = playlist.next()
            try:
                if isinstance(item, ImageItem):
                    logger.info("Image: %s", item.path.name)
                    img = Image.open(item.path)
                else:
                    logger.info("Quote: %s", item.author)
                    img = render_quote(item.text, item.author)
                screen.display(screen.get_buffer(img))
            except Exception:
                logger.exception("Failed to display item, skipping")
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Interrupted, sleeping display")
    finally:
        screen.sleep()


if __name__ == "__main__":
    main()
