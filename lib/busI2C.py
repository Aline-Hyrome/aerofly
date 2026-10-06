from machine import I2C


class BusI2C:
    """Cette classe à pour but de centraliser les objets de contrôle 
    du bus I2C.
    Elle permet d'utiliser 1 objet par bus I2C.
    """
    _instances = {}

    # Singleton
    def __new__(cls, bus: int, baudrate = 400000, pins = ("P9", "P10")):
        if bus not in cls._instances:
            cls._instances[bus] = super().__new__(cls)
        return cls._instances[bus]

    def __init__(self, bus: int, baudrate = 400000, pins = ("P9", "P10")) -> None:
        if not hasattr(self, '_BusI2C__i2c_bus'):
            self.__i2c_bus = I2C(bus, I2C.MASTER, baudrate=baudrate, pins=pins)
            self.__baudrate = baudrate
            self.__pins = pins

    @property
    def i2c_bus(self) -> I2C:
        return self.__i2c_bus

    @property
    def baudrate(self):
        return self.__baudrate

    @property
    def pins(self):
        return self.__pins
