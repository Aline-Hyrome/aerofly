from .composant import Composant
from utime import sleep_ms


class SHT3X(Composant):
    def __init__(self, i2c, address=0x44):  # Adresse du capteur
        self.i2c = i2c
        self.addr = address
        self.cmd_measure = b'\x24\x00'  # Mesure en mode "High repeatability, clock stretching disabled"

    def _check_crc(self, data):
        crc = 0xFF
        poly = 0x31
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = ((crc << 1) ^ poly) & 0xFF
                else:
                    crc = (crc << 1) & 0xFF
        return crc

    def temperature(self):
        self.i2c.writeto(self.addr, self.cmd_measure)
        sleep_ms(20)
        try:
            data = self.i2c.readfrom(self.addr, 6)
        except OSError:
            return 0.0
        temp_raw = data[0] << 8 | data[1]
        temp_crc = data[2]

        if self._check_crc(data[0:2]) != temp_crc:
            raise ValueError("CRC erreur température")

        temperature = -45 + (175 * temp_raw / 65535.0)
        return round(temperature, 2)

    def humidite(self):
        self.i2c.writeto(self.addr, self.cmd_measure)
        sleep_ms(20) # Voir si cela peut être réduit
        try:
            data = self.i2c.readfrom(self.addr, 6)
        except OSError:
            return 0.0
        hum_raw = data[3] << 8 | data[4]
        hum_crc = data[5]

        if self._check_crc(data[3:5]) != hum_crc:
            raise ValueError("CRC erreur humidité")

        humidity = 100 * hum_raw / 65535.0
        return round(humidity, 2)
