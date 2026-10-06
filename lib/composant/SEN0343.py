from .composant import Composant
import time
import math

class SEN0343(Composant):
    def __init__(self, i2c, adresse):
        self.i2c = i2c
        self.addresse = adresse
        self.pressure_offset = 0.0
        self.air_density = 1.225

        # Calibration initiale
        self.pressure_offset = self.get_data()[0]
        self.config_chip()

    def config_chip(self):
        """Envoie la trame de configuration au capteur."""
        self.i2c.writeto(self.addresse, b'\xAA\x00\x80')
        time.sleep(0.03)

    def read_data(self):
        """Lit les 7 octets de données du capteur via I2C."""
        data = memoryview(bytearray(7))
        self.i2c.readfrom_into(self.addresse, data)
        return data

    def get_data(self):
        """Récupère les valeurs de pression et température converties."""
        data = self.read_data()

        pressure_raw = ((data[1] << 8) | data[2]) >> 2
        temp_raw = (data[4] << 8) | data[5]

        pressure = (pressure_raw / 16384.0) * 1200 - 600 - self.pressure_offset
        temperature = (temp_raw / 65536.0) * 125 - 40

        return pressure, temperature

    def get_filtered_data(self):
        """Filtrage des valeurs en prenant la moyenne des 3 valeurs centrales."""
        pressures = sorted([self.get_data()[0] for _ in range(5)])[1:4]
        temperatures = sorted([self.get_data()[1] for _ in range(5)])[1:4]

        return sum(pressures) / 3, sum(temperatures) / 3
   
    def get_speed(self):
        """Calcule la vitesse de l'air à partir de la pression différentielle."""
        pressure, _ = self.get_filtered_data()
        if pressure > 0:
            return math.sqrt((2 * pressure) / self.air_density)
        return 0.0