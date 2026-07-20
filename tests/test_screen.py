import logging
from unittest.mock import patch

import pytest
from PIL import Image

from the_frame.waveshare_epd.screen import HEIGHT, WIDTH, Screen


@pytest.fixture
def screen():
    with patch("the_frame.waveshare_epd.screen.RaspberryPi") as MockRPi:
        MockRPi.return_value.digital_read.return_value = 1  # idle
        MockRPi.RST_PIN = 17
        MockRPi.DC_PIN = 25
        MockRPi.BUSY_PIN = 24
        MockRPi.PWR_PIN = 18
        yield Screen()


class TestGetBuffer:
    def test_landscape_input_correct_length(self, screen):
        # HEIGHT×WIDTH = 600×400 triggers the elif rotation branch
        img = Image.new("RGB", (HEIGHT, WIDTH))
        assert len(screen.get_buffer(img)) == WIDTH * HEIGHT // 2

    def test_buffer_length_is_120000(self, screen):
        # 400 * 600 / 2 = 120,000 bytes (2 pixels per byte)
        img = Image.new("RGB", (WIDTH, HEIGHT))
        assert len(screen.get_buffer(img)) == 120_000

    def test_all_nibbles_are_valid_color_indices(self, screen):
        # Each nibble must be 0–6 (the 7 Spectra 6 color slots)
        img = Image.new("RGB", (WIDTH, HEIGHT), "white")
        buf = screen.get_buffer(img)
        for i, byte in enumerate(buf):
            high = (byte >> 4) & 0xF
            low = byte & 0xF
            assert high <= 6, f"byte {i}: high nibble {high} out of range"
            assert low <= 6, f"byte {i}: low nibble {low} out of range"

    def test_white_image_nibbles_are_white_index(self, screen):
        # RGB (255,255,255) maps to palette index 1 (White)
        img = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
        buf = screen.get_buffer(img)
        expected_byte = (1 << 4) | 1  # 0x11
        assert all(b == expected_byte for b in buf)

    def test_wrong_size_logs_warning(self, screen, caplog):
        img = Image.new("RGB", (800, 600))
        with caplog.at_level(logging.WARNING, logger="the_frame.waveshare_epd.screen"):
            screen.get_buffer(img)
        assert caplog.records, "expected a warning for unsupported image size"
