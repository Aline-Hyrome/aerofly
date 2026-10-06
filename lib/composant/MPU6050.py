from machine import I2C
from busI2C import BusI2C
from capteur import Accelerometre, Gyroscope
from .composant import Composant

class MPU6050(Composant):
    """Classe MPU6050, classe permettant l'acquisition des données :
    - De l'accéléromètre 3 axes
    - Du gyroscope 3 axes
    """

    DEFAULT_I2C_ADDRESS = 0x68
    NON_DEFAULT_I2C_ADDRESS = 0x69

    WHO_AM_I_REGISTER = 0x75
    SIGNAL_PATH_RESET_REGISTER = 0x68

    # Les registres ci-dessous sont par 2 octets
    ACCEL_XOUT_H_REGISTER = 0x3B
    ACCEL_XOUT_L_REGISTER = 0x3C
    ACCEL_YOUT_H_REGISTER = 0x3D
    ACCEL_YOUT_L_REGISTER = 0x3E
    ACCEL_ZOUT_H_REGISTER = 0x3F
    ACCEL_ZOUT_L_REGISTER = 0x40

    TEMP_OUT_H_REGISTER = 0x41
    TEMP_OUT_L_REGISTER = 0x41

    GYRO_XOUT_H_REGISTER = 0x43
    GYRO_XOUT_L_REGISTER = 0x44
    GYRO_YOUT_H_REGISTER = 0x45
    GYRO_YOUT_L_REGISTER = 0x46
    GYRO_ZOUT_H_REGISTER = 0x47
    GYRO_ZOUT_L_REGISTER = 0x48

    #     BIT 7   | BIT 6 | BIT 5 | BIT 4 |  BIT 3  | BIT 2 | BIT 1 | BIT 0
    # DEVICE_RESET| SLEEP | CYCLE |   -   |TEMP_DIS |         CLKSEL
    # DEVICE_RESET When set to 1, this bit resets all internal registers to their default values.
    #              The bit automatically clears to 0 once the reset is done.
    #              The default values for each register can be found in Section 3.
    # SLEEP        When set to 1, this bit puts the MPU-60X0 into sleep mode.
    # CYCLE        When this bit is set to 1 and SLEEP is disabled, the MPU-60X0 will cycle
    #              between sleep mode and waking up to take a single sample of data from
    #              active sensors at a rate determined by LP_WAKE_CTRL (register 108).
    # TEMP_DIS     When set to 1, this bit disables the temperature sensor.
    # CLKSEL       3-bit unsigned value. Specifies the clock source of the device.

    AWAKE_REGISTER = 0x6B
    AWAKE_MODE_MPU_WITHOUT_TEMP = 0x10
    AWAKE_MODE_MPU_WITH_TEMP = 0x00
    ASLEEP_MODE_MPU = 0x48


    def __init__(self, adresse: int, bus_I2C: BusI2C | I2C) -> None:
        """Initialisation de la classe gérant le composant MPU6050

        :param adresse: Adresse du composant ADO Low = 0x68, ADO HIGH = 0x69
        :type adresse: int
        :param bus_i2c: Objet BusI2C
        :type bus_i2c: BusI2C
        """
        if adresse not in (self.DEFAULT_I2C_ADDRESS, self.NON_DEFAULT_I2C_ADDRESS):
            raise ValueError("Adresse I2C pour ce composant incorrect. Adresse données: %s" %adresse)

        self.adresse = adresse
        if isinstance(bus_I2C, BusI2C):
            self.__bus_I2C = bus_I2C.i2c_bus
        else:
            self.__bus_I2C = bus_I2C

        # Le MPU6050 est en sleep mode
        self.__sleep = 1
        self.__accel_X = 0
        self.__accel_Y = 0
        self.__accel_Z = 0
        self.__temp = 0
        self.__gyro_X = 0
        self.__gyro_Y = 0
        self.__gyro_Z = 0

        self.__test_connexion()

        # MPU6050 Awakening
        self.sleep = 0

    @property
    def sleep(self):
        return self.__sleep

    @sleep.setter
    def sleep(self, sleep_mode: bool):
        if sleep_mode:
            self.__bus_I2C.writeto_mem(self.adresse, self.AWAKE_REGISTER, self.ASLEEP_MODE_MPU)
        else:
            self.__bus_I2C.writeto_mem(self.adresse, self.AWAKE_REGISTER, self.AWAKE_MODE_MPU_WITHOUT_TEMP)

        self.__sleep = sleep_mode

    def __test_connexion(self):
        """Test la connexion avec le composant.

        :raises OSError: Le composant ne répond pas
        :return: Le composant répond
        :rtype: Litteral[True]
        """
        who_am_i = self.__bus_I2C.readfrom_mem(self.adresse, self.WHO_AM_I_REGISTER, 1)
        if int.from_bytes(who_am_i, "big") == self.adresse:
            return True
        raise OSError("Connexion au composant MPU6050 impossible")

    def __get_raw_values(self) -> bytes:
        """Récupère les valeurs des registres Accel, Temp, Gyro

        :return: Valeurs des registres
        :rtype: bytes
        """
        # 3B étant le registre de ACCEL_XOUT_H allant jusqu'à GYRO_ZOUT_L (14 octets)
        return self.__bus_I2C.readfrom_mem(self.adresse, self.ACCEL_XOUT_H_REGISTER, 14)

    def __bytes_toint(self, firstbyte, secondbyte) -> int:
        """Convertis des octets en entier

        :param firstbyte: _description_
        :type firstbyte: _type_
        :param secondbyte: _description_
        :type secondbyte: _type_
        :return: _description_
        :rtype: _type_
        """
        if not firstbyte & 0x80:
            return firstbyte << 8 | secondbyte
        return - (((firstbyte ^ 255) << 8) | (secondbyte ^ 255) + 1)

    def get_values(self) -> None:
        """Récupère les valeurs des registres et les converties en entier
        dans les attributs
        """
        raw_ints = self.__get_raw_values()
        self.__accel_X = self.__bytes_toint(raw_ints[0], raw_ints[1])
        self.__accel_Y = self.__bytes_toint(raw_ints[2], raw_ints[3])
        self.__accel_Z = self.__bytes_toint(raw_ints[4], raw_ints[5])
        # self.__temp = self.__bytes_toint(raw_ints[6], raw_ints[7]) / 340.00 + 36.53
        self.__gyro_X = self.__bytes_toint(raw_ints[8], raw_ints[9])
        self.__gyro_Y = self.__bytes_toint(raw_ints[10], raw_ints[11])
        self.__gyro_Z = self.__bytes_toint(raw_ints[12], raw_ints[13])

    def get_accelerometre(self) -> tuple[int, int, int]:
        """Récupère les données de l'acceléromètre issue de get_values()

        :return: Coordonnées: (x, y, z)
        :rtype: tuple[int, int, int]
        """
        return (self.__accel_X, self.__accel_Y, self.__accel_Z)

    def get_gyroscope(self) -> tuple[int, int, int]:
        """Récupère les données du gyroscope issue de get_values()

        :return: Coordonnées: (x, y, z)
        :rtype: tuple[int, int, int]
        """
        return (self.__gyro_X, self.__gyro_Y, self.__gyro_Z)

    @property
    def accel_X(self) -> float:
        """Getter pour l'accélération X

        :return: accélération X
        :rtype: float
        """
        return self.__accel_X

    @property
    def accel_Y(self) -> float:
        """Getter pour l'accélération Y

        :return: accélération Y
        :rtype: float
        """
        return self.__accel_Y

    @property
    def accel_Z(self) -> float:
        """Getter pour l'accélération Z

        :return: accélération Z
        :rtype: float
        """
        return self.__accel_Z

    @property
    def temp(self) -> float:
        """Getter pour la température

        :return: Température
        :rtype: float
        """
        return self.__temp

    @property
    def gyro_X(self) -> float:
        """Getter pour la vitesse angulaire X

        :return: vitesse angulaire X
        :rtype: float
        """
        return self.__gyro_X

    @property
    def gyro_Y(self) -> float:
        """Getter pour la vitesse angulaire Y

        :return: vitesse angulaire Y
        :rtype: float
        """
        return self.__gyro_Y

    @property
    def gyro_Z(self) -> float:
        """Getter pour la vitesse angulaire Z

        :return: vitesse angulaire Z
        :rtype: float
        """
        return self.__gyro_Z
