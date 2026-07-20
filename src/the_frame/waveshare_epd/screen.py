import logging

from PIL import Image

from .config import RaspberryPi

WIDTH = 400
HEIGHT = 600

logger = logging.getLogger(__name__)

# Spectra 6 E6 six-color palette. Index 4 is an unused slot that keeps
# the hardware color indices aligned (the controller skips that value).
_PALETTE_COLORS = [
    (0, 0, 0),  # 0 Black
    (255, 255, 255),  # 1 White
    (255, 255, 0),  # 2 Yellow
    (255, 0, 0),  # 3 Red
    (0, 0, 0),  # 4 (unused)
    (0, 0, 255),  # 5 Blue
    (0, 255, 0),  # 6 Green
]
_PALETTE = tuple(v for rgb in _PALETTE_COLORS for v in rgb) + (0, 0, 0) * 249


class Screen:
    width = WIDTH
    height = HEIGHT

    def __init__(self):
        self._pi = RaspberryPi()

    # -------------------------------------------------------------------------
    # Low-level SPI / GPIO
    # -------------------------------------------------------------------------

    def _write(self, dc, data):
        self._pi.digital_write(RaspberryPi.DC_PIN, dc)
        self._pi.spi_write(data)

    def _cmd(self, command):
        self._write(0, [command])

    def _data(self, data):
        self._write(1, [data])

    def _bulk(self, data):
        self._write(1, data)

    def _reset(self):
        self._pi.digital_write(RaspberryPi.RST_PIN, 1)
        self._pi.delay_ms(20)
        self._pi.digital_write(RaspberryPi.RST_PIN, 0)
        self._pi.delay_ms(2)
        self._pi.digital_write(RaspberryPi.RST_PIN, 1)
        self._pi.delay_ms(20)

    def _wait_idle(self):
        while self._pi.digital_read(RaspberryPi.BUSY_PIN) == 0:  # 0: busy, 1: idle
            self._pi.delay_ms(5)

    def _power_cycle_refresh(self):
        self._cmd(0x04)  # POWER_ON
        self._wait_idle()
        self._cmd(0x12)  # DISPLAY_REFRESH
        self._data(0x00)
        self._wait_idle()
        self._cmd(0x02)  # POWER_OFF
        self._data(0x00)
        self._wait_idle()

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def init(self):
        self._pi.open()
        self._reset()
        self._wait_idle()
        self._pi.delay_ms(30)

        self._cmd(0xAA)
        self._data(0x49)
        self._data(0x55)
        self._data(0x20)
        self._data(0x08)
        self._data(0x09)
        self._data(0x18)

        self._cmd(0x01)
        self._data(0x3F)

        self._cmd(0x00)
        self._data(0x5F)
        self._data(0x69)

        self._cmd(0x03)
        self._data(0x00)
        self._data(0x54)
        self._data(0x00)
        self._data(0x44)

        self._cmd(0x05)
        self._data(0x40)
        self._data(0x1F)
        self._data(0x1F)
        self._data(0x2C)

        self._cmd(0x06)
        self._data(0x6F)
        self._data(0x1F)
        self._data(0x17)
        self._data(0x49)

        self._cmd(0x08)
        self._data(0x6F)
        self._data(0x1F)
        self._data(0x1F)
        self._data(0x22)

        self._cmd(0x30)
        self._data(0x03)

        self._cmd(0x50)
        self._data(0x3F)

        self._cmd(0x60)
        self._data(0x02)
        self._data(0x00)

        # Panel resolution: 400 x 600
        self._cmd(0x61)
        self._data(0x01)
        self._data(0x90)  # 0x0190 = 400
        self._data(0x02)
        self._data(0x58)  # 0x0258 = 600

        self._cmd(0x84)
        self._data(0x01)

        self._cmd(0xE3)
        self._data(0x2F)

        self._cmd(0x04)  # POWER_ON — panel is ready after this
        self._wait_idle()

    def get_buffer(self, image):
        pal = Image.new("P", (1, 1))
        pal.putpalette(_PALETTE)

        if image.size == (WIDTH, HEIGHT):
            source = image
        elif image.size == (HEIGHT, WIDTH):
            source = image.rotate(90, expand=True)
        else:
            logger.warning(
                "Image size %dx%d doesn't match display %dx%d — resizing to fit",
                *image.size,
                WIDTH,
                HEIGHT,
            )
            source = image.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

        quantized = source.convert("RGB").quantize(palette=pal)
        raw = bytearray(quantized.tobytes("raw"))

        buf = bytearray(WIDTH * HEIGHT // 2)
        for i in range(0, len(raw), 2):
            buf[i // 2] = (raw[i] << 4) | raw[i + 1]

        return buf

    def display(self, buf):
        self._cmd(0x10)
        self._bulk(buf)
        self._power_cycle_refresh()

    def clear(self, color=0x11):
        self._cmd(0x10)
        self._bulk(bytes([color]) * (HEIGHT * WIDTH // 2))
        self._power_cycle_refresh()

    def sleep(self):
        self._cmd(0x07)  # DEEP_SLEEP
        self._data(0xA5)
        self._pi.delay_ms(2000)
        self._pi.close()
