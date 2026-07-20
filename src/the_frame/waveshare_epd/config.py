import time


class RaspberryPi:
    RST_PIN = 17
    DC_PIN = 25
    BUSY_PIN = 24
    PWR_PIN = 18

    def __init__(self):
        import gpiozero
        import spidev

        self._spi = spidev.SpiDev()
        self._rst = gpiozero.LED(self.RST_PIN)
        self._dc = gpiozero.LED(self.DC_PIN)
        self._pwr = gpiozero.LED(self.PWR_PIN)
        self._busy = gpiozero.Button(self.BUSY_PIN, pull_up=False)
        self._gpio_map = {
            self.RST_PIN: self._rst,
            self.DC_PIN: self._dc,
            self.PWR_PIN: self._pwr,
        }

    def digital_write(self, pin, value):
        if pin in self._gpio_map:
            self._gpio_map[pin].on() if value else self._gpio_map[pin].off()

    def digital_read(self, pin):
        if pin == self.BUSY_PIN:
            return self._busy.value
        return 0

    def delay_ms(self, ms):
        time.sleep(ms / 1000.0)

    def spi_write(self, data):
        self._spi.writebytes2(data)

    def open(self):
        self._pwr.on()
        self._spi.open(0, 0)
        self._spi.max_speed_hz = 4_000_000
        self._spi.mode = 0b00

    def close(self, cleanup=False):
        self._spi.close()
        self._rst.off()
        self._dc.off()
        self._pwr.off()
        if cleanup:
            self._rst.close()
            self._dc.close()
            self._pwr.close()
            self._busy.close()
