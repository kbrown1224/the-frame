from PIL import Image
from image_converter import prepare_image
from waveshare_epd.screen import Screen
import tempfile, os

IMG_PATH = "input_images/fam_at_pond.png"

with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
    tmp_path = tmp.name

try:
    prepare_image(IMG_PATH, tmp_path)
    img = Image.open(tmp_path)

    screen = Screen()
    screen.init()
    screen.display(screen.getbuffer(img))
    screen.sleep()
finally:
    os.unlink(tmp_path)
