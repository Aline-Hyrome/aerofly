from machine import I2C, Pin
import time

class BMS:
    """Classe du composant INA3221
    Permet de récupérer la tension du bus et du shunt 
    afin de déterminé l'intensité et la tension en un point du circuit
    """

    __INA3221_ADDR = 0x40

    __REG_CONFIG = 0x00
    __REG_SHUNT_VOLTAGE_1 = 0x01
    __REG_BUS_VOLTAGE_1 = 0x02
    __REG_SHUNT_VOLTAGE_2 = 0x03
    __REG_BUS_VOLTAGE_2 = 0x04
    __REG_SHUNT_VOLTAGE_3 = 0x05
    __REG_BUS_VOLTAGE_3 = 0x06

    __RES_INT = 0.1
    
    __i2c = I2C(0) 

    def __init__(self):
        """
        Instanciation de la classe BMS
        """
        self.__canal1 = []
        self.__canal2 = []
        self.__canal3 = []

    def __scan_i2c(self):
        """
        Fonction pour scanner l'I2C
        """
        devices = self.__i2c.scan()
        if devices:
            print("Peripheriques trouves sur le bus I2C :")
            for device in devices:
                print("Adresse : 0x{:02X}".format(device))
        else:
            print("Aucun périphérique trouvé sur le bus I2C.")

    def __read_register(self,reg):
        """
        Fonction pour lire un registre 16 bits du INA3221
        Lire 2 octets du registre
        Convertir les données en un entier 16 bits (big-endian)
        """
        data = self.__i2c.readfrom_mem(self.__INA3221_ADDR, reg, 2)
        value = (data[0] << 8) | data[1]
        return value
        
    def __configure_ina3221(self):
        """
        Fonction pour configurer le INA3221
        Configuration par défaut : mode continu, calibration
        """
        config = 0x7127  
        self.__i2c.writeto_mem(self.__INA3221_ADDR, self.__REG_CONFIG, bytearray([config >> 8, config & 0xFF]))

    def __read_channel_data(self,channel):
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
        ampere = shunt_voltage / self.__RES_INT

        return shunt_voltage, bus_voltage, ampere

    def main_tension(self):
        """
        Scanner le bus I2C pour vérifier les périphériques connectés
        Si l'INA3221 est trouvé, on procède à la configuration et à la lecture des données
        """
        self.__scan_i2c()


        self.__configure_ina3221()

        shunt_voltage_1, bus_voltage_1, ampere_1 = self.__read_channel_data(1)
        self.__canal1.append(bus_voltage_1), self.__canal1.append(ampere_1)
        print("Canal 1 - Tension shunt: {:.3f}V, Tension bus: {:.3f}V, Ampere: {:.3f}A".format(shunt_voltage_1, bus_voltage_1,ampere_1))
        
        shunt_voltage_2, bus_voltage_2, ampere_2 = self.__read_channel_data(2)
        self.__canal1.append(bus_voltage_2), self.__canal1.append(ampere_2)
        print("Canal 2 - Tension shunt: {:.3f}V, Tension bus: {:.3f}V, Ampere: {:.3f}A".format(shunt_voltage_2, bus_voltage_2,ampere_2))
        
        shunt_voltage_3, bus_voltage_3, ampere_3 = self.__read_channel_data(3)
        self.__canal1.append(bus_voltage_3), self.__canal1.append(ampere_3)
        print("Canal 3 - Tension shunt: {:.3f}V, Tension bus: {:.3f}V, Ampere: {:.3f}A".format(shunt_voltage_3, bus_voltage_3,ampere_3))
        
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

if __name__ == "__main__":    
    tension = BMS()
    tension.main_tension()
    print(tension.get_canal1())
