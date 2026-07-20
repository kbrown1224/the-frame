from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

DISPLAY_WIDTH = 600
DISPLAY_HEIGHT = 400
SATURATION_BOOST = 1.5
CONTRAST_BOOST = 1.5
VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"}


def process_images(source_dir, output_dir):
    source_dir = Path(source_dir)
    output_dir = Path(output_dir)
    for path in sorted(source_dir.iterdir()):
        if path.name.startswith("."):
            continue
        if path.is_file() and path.suffix.lower() in VALID_EXTENSIONS:
            print(f"Processing: {path.name}")
            prepare_image(path, output_dir / path.name)


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

        cropped = ImageEnhance.Color(cropped).enhance(SATURATION_BOOST)
        cropped = ImageEnhance.Contrast(cropped).enhance(CONTRAST_BOOST)

        cropped.save(out_path)
        print(f"  Saved to {out_path}")


if __name__ == "__main__":
    process_images(source_dir=Path("input_images"), output_dir=Path("images"))
