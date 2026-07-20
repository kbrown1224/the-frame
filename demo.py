import tempfile
from pathlib import Path

from PIL import Image

from the_frame.image_converter import prepare_image
from the_frame.waveshare_epd.screen import Screen

IMG_PATH = Path("input_images/fam_at_pond.png")

with tempfile.TemporaryDirectory() as tmp_dir:
    tmp_path = Path(tmp_dir) / "processed.png"
    prepare_image(IMG_PATH, tmp_path)
    with Image.open(tmp_path) as img:
        screen = Screen()
        screen.init()
        screen.display(screen.get_buffer(img))
        screen.sleep()
