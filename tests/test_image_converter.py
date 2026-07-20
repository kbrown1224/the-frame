import pytest
from PIL import Image

from the_frame.image_converter import (
    DISPLAY_HEIGHT,
    DISPLAY_WIDTH,
    prepare_image,
    process_images,
)


def _make_image(path):
    Image.new("RGB", (800, 600), "white").save(path)


@pytest.fixture
def out_dir(tmp_path):
    d = tmp_path / "out"
    d.mkdir()
    return d


class TestPrepareImage:
    def test_output_size_landscape_input(self, tmp_path):
        Image.new("RGB", (1200, 800), "red").save(tmp_path / "in.jpg")
        prepare_image(tmp_path / "in.jpg", tmp_path / "out.jpg")
        assert Image.open(tmp_path / "out.jpg").size == (DISPLAY_WIDTH, DISPLAY_HEIGHT)

    def test_output_size_portrait_input(self, tmp_path):
        Image.new("RGB", (300, 900), "blue").save(tmp_path / "in.jpg")
        prepare_image(tmp_path / "in.jpg", tmp_path / "out.jpg")
        assert Image.open(tmp_path / "out.jpg").size == (DISPLAY_WIDTH, DISPLAY_HEIGHT)

    def test_output_size_square_input(self, tmp_path):
        Image.new("RGB", (500, 500), "green").save(tmp_path / "in.jpg")
        prepare_image(tmp_path / "in.jpg", tmp_path / "out.jpg")
        assert Image.open(tmp_path / "out.jpg").size == (DISPLAY_WIDTH, DISPLAY_HEIGHT)

    def test_output_size_exact_display_dimensions(self, tmp_path):
        Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT), "white").save(tmp_path / "in.jpg")
        prepare_image(tmp_path / "in.jpg", tmp_path / "out.jpg")
        assert Image.open(tmp_path / "out.jpg").size == (DISPLAY_WIDTH, DISPLAY_HEIGHT)

    def test_enhancement_changes_pixels(self, tmp_path):
        Image.new("RGB", (600, 400), (100, 150, 80)).save(tmp_path / "in.png")
        prepare_image(tmp_path / "in.png", tmp_path / "out.png")
        result = Image.open(tmp_path / "out.png").convert("RGB")
        assert result.getpixel((300, 200)) != (100, 150, 80)


class TestProcessImages:
    def test_skips_dotfiles(self, tmp_path, out_dir):
        (tmp_path / ".hidden.jpg").write_bytes(b"not a real image")
        process_images(tmp_path, out_dir)
        assert list(out_dir.iterdir()) == []

    def test_skips_non_image_extensions(self, tmp_path, out_dir):
        (tmp_path / "notes.txt").write_text("hello")
        (tmp_path / "data.csv").write_text("a,b,c")
        process_images(tmp_path, out_dir)
        assert list(out_dir.iterdir()) == []

    def test_handles_empty_directory(self, tmp_path, out_dir):
        process_images(tmp_path, out_dir)
        assert list(out_dir.iterdir()) == []

    def test_processes_jpg(self, tmp_path, out_dir):
        _make_image(tmp_path / "photo.jpg")
        process_images(tmp_path, out_dir)
        assert (out_dir / "photo.jpg").exists()

    def test_processes_png(self, tmp_path, out_dir):
        _make_image(tmp_path / "photo.png")
        process_images(tmp_path, out_dir)
        assert (out_dir / "photo.png").exists()

    def test_processes_multiple_files(self, tmp_path, out_dir):
        for name in ["a.jpg", "b.png", "c.jpeg"]:
            _make_image(tmp_path / name)
        process_images(tmp_path, out_dir)
        assert len(list(out_dir.iterdir())) == 3

    def test_output_images_are_correct_size(self, tmp_path, out_dir):
        _make_image(tmp_path / "photo.jpg")
        process_images(tmp_path, out_dir)
        assert Image.open(out_dir / "photo.jpg").size == (DISPLAY_WIDTH, DISPLAY_HEIGHT)
