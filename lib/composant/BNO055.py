from time import sleep

import ustruct
from busI2C import BusI2C
from micropython import const

from .composant import Composant


class BNO055(Composant):
    # FROM https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bno055-ds000.pdf
    """
    L'I2C du composant BNO055 ne supporte que des adresses 7-bits
    Configuration I2C: 

    f: 400 kHz
    SCL_LOW_MIN = 1.3 μs
    SCL_MAX_MIN = 0.6 μs

    IDLE_TIME_LOW_PWR_MODE_2 = 2 μs
    IDLE_TIME_LOW_PWR_MODE_1 = 450 μs

    I2C Config | COM3_state | I2C address
    -----------+------------+------------
       slave   |    HIGH    |     0x29
       slave   |     LOW    |     0x28
    """
    BNO055_ALT_ADDRESS = 0x29 # 0b0101001
    BNO055_DEFAULT_ADDRESS = 0x28 # 0b0101000
    BNO055_CHIP_ID = const(0xA0)

    # Idle time between write, accesses, normal mode, standby mode, low-power mode 2
    IDLE_TIME_LOW_PWR_MODE_2 = 2 * 10 ** (-6)
    # Idle time between write, accesses, suspend mode, low-power mode 1
    IDLE_TIME_LOW_PWR_MODE_1 = 450 * 10 ** (-6)

    # REGISTRE

    # PAGE0 REGISTER DEFINITION STAR
    BNO055_CHIP_ID_ADDR = 0x00
    BNO055_ACCEL_REV_ID_ADDR = 0x01
    BNO055_MAG_REV_ID_ADDR = 0x02
    BNO055_GYRO_REV_ID_ADDR = 0x03
    BNO055_SW_REV_ID_LSB_ADDR = 0x04
    BNO055_SW_REV_ID_MSB_ADDR = 0x05
    BNO055_BL_REV_ID_ADDR = 0x06
    BNO055_PAGE_ID_ADDR = 0x07

    # Accel data register
    BNO055_ACCEL_DATA_X_LSB_ADDR = 0x08
    BNO055_ACCEL_DATA_X_MSB_ADDR = 0x09
    BNO055_ACCEL_DATA_Y_LSB_ADDR = 0x0A
    BNO055_ACCEL_DATA_Y_MSB_ADDR = 0x0B
    BNO055_ACCEL_DATA_Z_LSB_ADDR = 0x0C
    BNO055_ACCEL_DATA_Z_MSB_ADDR = 0x0D

    # Mag data register
    BNO055_MAG_DATA_X_LSB_ADDR = 0x0E
    BNO055_MAG_DATA_X_MSB_ADDR = 0x0F
    BNO055_MAG_DATA_Y_LSB_ADDR = 0x10
    BNO055_MAG_DATA_Y_MSB_ADDR = 0x11
    BNO055_MAG_DATA_Z_LSB_ADDR = 0x12
    BNO055_MAG_DATA_Z_MSB_ADDR = 0x13

    # Gyro data registers
    BNO055_GYRO_DATA_X_LSB_ADDR = 0x14
    BNO055_GYRO_DATA_X_MSB_ADDR = 0x15
    BNO055_GYRO_DATA_Y_LSB_ADDR = 0x16
    BNO055_GYRO_DATA_Y_MSB_ADDR = 0x17
    BNO055_GYRO_DATA_Z_LSB_ADDR = 0x18
    BNO055_GYRO_DATA_Z_MSB_ADDR = 0x19

    # Euler data registers
    BNO055_EULER_H_LSB_ADDR = 0x1A
    BNO055_EULER_H_MSB_ADDR = 0x1B
    BNO055_EULER_R_LSB_ADDR = 0x1C
    BNO055_EULER_R_MSB_ADDR = 0x1D
    BNO055_EULER_P_LSB_ADDR = 0x1E
    BNO055_EULER_P_MSB_ADDR = 0x1F

    # Quaternion data registers
    BNO055_QUATERNION_DATA_W_LSB_ADDR = 0x20
    BNO055_QUATERNION_DATA_W_MSB_ADDR = 0x21
    BNO055_QUATERNION_DATA_X_LSB_ADDR = 0x22
    BNO055_QUATERNION_DATA_X_MSB_ADDR = 0x23
    BNO055_QUATERNION_DATA_Y_LSB_ADDR = 0x24
    BNO055_QUATERNION_DATA_Y_MSB_ADDR = 0x25
    BNO055_QUATERNION_DATA_Z_LSB_ADDR = 0x26
    BNO055_QUATERNION_DATA_Z_MSB_ADDR = 0x27

    # Linear acceleration data registers
    BNO055_LINEAR_ACCEL_DATA_X_LSB_ADDR = 0x28
    BNO055_LINEAR_ACCEL_DATA_X_MSB_ADDR = 0x29
    BNO055_LINEAR_ACCEL_DATA_Y_LSB_ADDR = 0x2A
    BNO055_LINEAR_ACCEL_DATA_Y_MSB_ADDR = 0x2B
    BNO055_LINEAR_ACCEL_DATA_Z_LSB_ADDR = 0x2C
    BNO055_LINEAR_ACCEL_DATA_Z_MSB_ADDR = 0x2D

    # Gravity data registers
    BNO055_GRAVITY_DATA_X_LSB_ADDR = 0x2E
    BNO055_GRAVITY_DATA_X_MSB_ADDR = 0x2F
    BNO055_GRAVITY_DATA_Y_LSB_ADDR = 0x30
    BNO055_GRAVITY_DATA_Y_MSB_ADDR = 0x31
    BNO055_GRAVITY_DATA_Z_LSB_ADDR = 0x32
    BNO055_GRAVITY_DATA_Z_MSB_ADDR = 0x33

    # Mode registers
    BNO055_OPR_MODE_ADDR = 0x3D
    BNO055_PWR_MODE_ADDR = 0x3E

    BNO055_SYS_TRIGGER_ADDR = 0x3F
    BNO055_TEMP_SOURCE_ADDR = 0x40

    # Values
    OPERATION_MODE_CONFIG = 0b0000
    OPERATION_MODE_NDOF = 0b1100

    POWER_MODE_NORMAL = 0b00

    def __init__(self, adresse: int, bus_I2C: BusI2C) -> None:
        """Constructeur de la classe BNO055

        :param adresse: Adresse I2C du composant defaut=0x28, alt=0x29
        :type adresse: int
        :param bus_I2C: Bus I2C
        :type bus_I2C: BusI2C
        :raises ValueError: Adresse I2C pour ce composant incorrect
        :raises RuntimeError: Mauvais ID de composant
        :raises RuntimeError: Le composant n'a pas répondu
        """
        if adresse not in (self.BNO055_DEFAULT_ADDRESS, self.BNO055_ALT_ADDRESS):
            raise ValueError("Adresse I2C pour ce composant incorrect. Adresse données: %s" %adresse)

        self.adresse = adresse
        self._last_euler_values = [0.0, 0.0, 0.0]

        self.__bus = bus_I2C

        chip_id = self.read_register(0x00, 1)

        if chip_id is None:
            raise RuntimeError("Le composant n'a pas répondu.")

        if int.from_bytes(chip_id, "little") != self.BNO055_CHIP_ID:
            raise RuntimeError("Mauvais ID de composant : %s au lieu de %s" %(chip_id, self.BNO055_CHIP_ID))

        self.set_mode(self.OPERATION_MODE_CONFIG)
        sleep(0.025)
        self.set_power_mode(self.POWER_MODE_NORMAL)
        sleep(0.1)

        self.set_page_id(0)

        self.set_mode(self.OPERATION_MODE_NDOF)
        sleep(0.1)
        self.__calibration()

    def __calibration(self):
        roll_data = []
        pitch_data = []

        for _ in range(300):
            _, roll, pitch = self.euler()
            roll_data.append(roll)
            pitch_data.append(pitch)

        self._roll_offset = sum(roll_data) / len(roll_data)
        self._pitch_offset = sum(pitch_data) / len(pitch_data)

    def set_power_mode(self, mode: int) -> bool:
        """
        Pour plus d'information sur les modes d'opération voir 
        table 3-1 dans la fiche technique du BNO055

             Normal    | 0b00
        ---------------+------
        Low Power Mode | 0b01
        ---------------+------
          Suspend Mode | 0b10

        :param mode: power mode
        :type mode: int
        :return: Succes de l'opération 
        :rtype: bool
        """
        if mode >= 0b00 and mode <= 0b10:
            self.write_register(self.BNO055_PWR_MODE_ADDR, mode)
            sleep(self.IDLE_TIME_LOW_PWR_MODE_2)
            return True
        return False

    def set_mode(self, mode: int) -> bool:
        """
        Pour plus d'information sur les modes d'opération voir 
        table 3-5 dans la fiche technique du BNO055
        :param mode: operating mode
        :type mode: int
        :return: Succes de l'opération 
        :rtype: bool
        """
        if 0b1100 >= mode >= 0b0000:
            self.write_register(self.BNO055_OPR_MODE_ADDR, mode)
            sleep(self.IDLE_TIME_LOW_PWR_MODE_2)
            return True
        return False

    def set_page_id(self, page_id: int) -> bool:
        """Selectionne la page sur le BNO055

        :param page_id: page_id
        :type page_id: int
        :return: Etat de l'opération
        :rtype: bool
        """
        if page_id not in [1, 2]:
            return False

        self.write_register(self.BNO055_PAGE_ID_ADDR, page_id)
        return True

    def read_register(self, register: int, length = 2) -> bytes | None:
        """Permet de lire un registre

        :param register: registre
        :type register: int
        :param length: longueur des données à lire en octet, defaults to 2
        :type length: int, optional
        :return: Données reçu ou None si echoué
        :rtype: bytes | None
        """
        try_counter = 1
        try:
            return self.__bus.readfrom_mem(self.adresse, register, length)
        except OSError:
            try:
                return self.__bus.readfrom(self.adresse, length)
            except OSError:
                try_counter -= 1
                return None

    def write_register(self, register: int, length = 2) -> None:
        """Ecrit sur un registre

        :param register: registre
        :type register: int
        :param length: longueur des données à lire en octet, defaults to 2
        :type length: int, optional
        """
        try_counter = 1
        try:
            self.__bus.writeto_mem(self.adresse, register, length)
        except OSError:
            try_counter -= 1
            return None

    def euler(self) -> list:
        """Les angles d'euler
        yaw data, roll data, pitch data

        :return: yaw, roll, pitch
        :rtype: list
        """
        bytes_value = self.read_register(self.BNO055_EULER_H_LSB_ADDR, 6)
        # b"\xa0\xfb2\x0f\x11\x03" dans de rare cas le composant envoie cette valeur incohérente :/
        if bytes_value is None or len(bytes_value) != 6 or bytes_value == b"\xa0\xfb2\x0f\x11\x03":
            return self._last_euler_values

        valeur = ustruct.unpack("<hhh", bytes_value)

        data = list(x / 16 for x in valeur)

        if data == [0.0, 0.0, 0.0]:
            self.set_mode(self.OPERATION_MODE_NDOF)
            return self._last_euler_values
        
        if hasattr(self, "_roll_offset") or hasattr(self, "_pitch_offset"):
            data[1] -= self._roll_offset
            data[2] -= self._pitch_offset
        self._last_euler_values = data
        return data
