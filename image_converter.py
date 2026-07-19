import os
from PIL import Image, ImageEnhance, ImageOps

DISPLAY_WIDTH = 400
DISPLAY_HEIGHT = 600

VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')


def process_images(source_dir, output_dir):
    for filename in os.listdir(source_dir):
        if filename.startswith('.'):
            continue

        filepath = os.path.join(source_dir, filename)
        if os.path.isfile(filepath) and filename.lower().endswith(VALID_EXTENSIONS):
            print(f"Processing: {filename}")
            prepare_image(filepath, os.path.join(output_dir, filename))


def prepare_image(img_path, out_path):
    with Image.open(img_path) as img:
        img = ImageOps.exif_transpose(img)

        orig_ratio = img.width / img.height
        target_ratio = DISPLAY_WIDTH / DISPLAY_HEIGHT

        if orig_ratio > target_ratio:
            new_width = int(DISPLAY_HEIGHT * orig_ratio)
            new_height = DISPLAY_HEIGHT
        else:
            new_width = DISPLAY_WIDTH
            new_height = int(DISPLAY_WIDTH / orig_ratio)

        resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        left = (new_width - DISPLAY_WIDTH) // 2
        top = (new_height - DISPLAY_HEIGHT) // 2
        cropped = resized.crop((left, top, left + DISPLAY_WIDTH, top + DISPLAY_HEIGHT))

        cropped = ImageEnhance.Color(cropped).enhance(1.5)
        cropped = ImageEnhance.Contrast(cropped).enhance(1.5)

        cropped.save(out_path)
        print(f"  Saved to {out_path}")


if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    process_images(
        source_dir=os.path.join(SCRIPT_DIR, "images"),
        output_dir=os.path.join(SCRIPT_DIR, "preview"),
    )
