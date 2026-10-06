from .composant import Composant
from busI2C import BusI2C

class INA3221(Composant):
    """Classe du composant INA3221
    Permet de récupérer la tension du bus et du shunt 
    afin de déterminé l'intensité et la tension en un point du circuit
    """
    __REG_CONFIG = 0x00
    __REG_SHUNT_VOLTAGE_1 = 0x01
    __REG_BUS_VOLTAGE_1 = 0x02
    __REG_SHUNT_VOLTAGE_2 = 0x03
    __REG_BUS_VOLTAGE_2 = 0x04
    __REG_SHUNT_VOLTAGE_3 = 0x05
    __REG_BUS_VOLTAGE_3 = 0x06

    def __init__(self, bus_i2c: BusI2C, adresse: int) -> None:
        """
        Instanciation de la classe BMS
        """
        self.__bus_i2c = bus_i2c
        self.__adresse = adresse
        self.__canal1 = []
        self.__canal2 = []
        self.__canal3 = []
        self.__configure_ina3221()

    def __read_register(self,reg):
        """
        Fonction pour lire un registre 16 bits du INA3221
        Lire 2 octets du registre
        Convertir les données en un entier 16 bits (big-endian)
        """
        data = self.__bus_i2c.readfrom_mem(self.__adresse, reg, 2)
        value = (data[0] << 8) | data[1]
        return value
        
    def __configure_ina3221(self):
        """
        Fonction pour configurer le INA3221
        Configuration par défaut : mode continu, calibration
        Configuration: Reset=pas de reset (0),AVG=16 (010), VBUS CT=1.1ms (100), VSHUNT CT=1.1ms (100), mode=Shunt+Bus continuous (111), mode=Bus continuous(110)
        """
        config = 0x4126   # ou 0x5127 ou 0x1127 ou 0x7127
        self.__bus_i2c.writeto_mem(self.__adresse, self.__REG_CONFIG, bytearray([config >> 8, config & 0xFF]))

    def read_channel_data(self, channel: int):
        """
        Lire les valeurs de la tension de bus et du courant (chaque canal)
        """
        if channel == 1:
            shunt_voltage = self.__read_register(self.__REG_SHUNT_VOLTAGE_1)
            bus_voltage = self.__read_register(self.__REG_BUS_VOLTAGE_1)
        elif channel == 2:
            shunt_voltage = self.__read_register(self.__REG_SHUNT_VOLTAGE_2)
            bus_voltage = self.__read_register(self.__REG_BUS_VOLTAGE_2)
        elif channel == 3:
            shunt_voltage = self.__read_register(self.__REG_SHUNT_VOLTAGE_3)
            bus_voltage = self.__read_register(self.__REG_BUS_VOLTAGE_3)

        shunt_voltage = shunt_voltage * 0.0025
        bus_voltage = bus_voltage * 0.001

        return bus_voltage, shunt_voltage

    def main_tension(self):
        """
        Scanner le bus I2C pour vérifier les périphériques connectés
        Si l'INA3221 est trouvé, on procède à la configuration et à la lecture des données
        """
        self.__canal1 = self.read_channel_data(1)
        self.__canal2 = self.read_channel_data(2)
        self.__canal3 = self.read_channel_data(3)

    def get_canal1(self):
        """
        Getter pour récupérer les donnees du canal 1
        """
        return self.__canal1
    
    def get_canal2(self):
        """
        Getter pour récupérer les donnees du canal 2
        """
        return self.__canal2
    
    def get_canal3(self):
        """
        Getter pour récupérer les donnees du canal 3
        """
        return self.__canal3

