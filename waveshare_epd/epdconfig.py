import logging
import time
import spidev
import gpiozero

logger = logging.getLogger(__name__)


class RaspberryPi:
    RST_PIN  = 17
    DC_PIN   = 25
    CS_PIN   = 8
    BUSY_PIN = 24
    PWR_PIN  = 18

    def __init__(self):


        self.SPI = spidev.SpiDev()
        self.GPIO_RST_PIN  = gpiozero.LED(self.RST_PIN)
        self.GPIO_DC_PIN   = gpiozero.LED(self.DC_PIN)
        self.GPIO_PWR_PIN  = gpiozero.LED(self.PWR_PIN)
        self.GPIO_BUSY_PIN = gpiozero.Button(self.BUSY_PIN, pull_up=False)

    def digital_write(self, pin, value):
        gpio_map = {
            self.RST_PIN: self.GPIO_RST_PIN,
            self.DC_PIN:  self.GPIO_DC_PIN,
            self.PWR_PIN: self.GPIO_PWR_PIN,
        }
        if pin in gpio_map:
            gpio_map[pin].on() if value else gpio_map[pin].off()

    def digital_read(self, pin):
        if pin == self.BUSY_PIN:
            return self.GPIO_BUSY_PIN.value
        return 0

    def delay_ms(self, ms):
        time.sleep(ms / 1000.0)

    def spi_writebyte(self, data):
        self.SPI.writebytes(data)

    def spi_writebyte2(self, data):
        self.SPI.writebytes2(data)

    def module_init(self, cleanup=False):
        self.GPIO_PWR_PIN.on()
        self.SPI.open(0, 0)
        self.SPI.max_speed_hz = 4000000
        self.SPI.mode = 0b00
        return 0

    def module_exit(self, cleanup=False):
        self.SPI.close()
        self.GPIO_RST_PIN.off()
        self.GPIO_DC_PIN.off()
        self.GPIO_PWR_PIN.off()
        if cleanup:
            self.GPIO_RST_PIN.close()
            self.GPIO_DC_PIN.close()
            self.GPIO_PWR_PIN.close()
            self.GPIO_BUSY_PIN.close()


