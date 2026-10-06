from .base_test import test
from machine import I2C
from micropython import const

class TestBNO055:

    def __init__(self) -> None:
        test(self.test_who_am_i(), "test_who_am_i")

    def test_who_am_i(self):
        adresse = 0x28
        i2c = I2C(0, baudrate=20000, pins=["P9","P8"])
        try:
            chip_id = i2c.readfrom_mem(adresse, 0x00, 1)
        except OSError:
            return False

        try:
            if int.from_bytes(chip_id, "little") != const(0xA0):
                return False
        except TypeError:
            return False
        return True

if __name__ == "__main__":
    TestBNO055()