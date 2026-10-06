from micropython import const
from time import sleep_ms
from .composant import Composant

class DFR_GNSS_I2C(Composant):
    """
    MicroPython class for communication with the GNSS receiver module from DFRobot via I2C
    """

    GNSS_DEVICE_ADDR = const(0x66)

    MODE_GPS = const(0x01)
    MODE_BEIDOU = const(0x02)
    MODE_GPS_BEIDOU = const(0x03)
    MODE_GLONASS = const(0x04)
    MODE_GPS_GLONASS = const(0x05)
    MODE_BEIDOU_GLONASS = const(0x06)
    MODE_GPS_BEIDOU_GLONASS = const(0x07)

    ENABLE_POWER = const(0x00)
    DISABLE_POWER = const(0x01)

    I2C_HOUR = const(0x04)
    I2C_LAT_1 = const(0x07)
    I2C_LON_1 = const(0x0D)
    I2C_USE_STAR = const(0x13)
    I2C_ALT_H = const(0x14)
    I2C_GNSS_MODE = const(0x22)
    I2C_SLEEP_MODE = const(0x23)

    def __init__(self, i2c, i2c_addr=GNSS_DEVICE_ADDR):
        """
        Initialize the DFRobot_GNSS communication
        :param i2c_addr: I2C address
        :param i2c_bus: I2C bus number
        """
        self.__i2c = i2c
        self.__addr = i2c_addr
        self.set_gnss_mode(MODE_GPS)
        self.set_enable_power()

        self._last_valid_lon = 0
        self._last_valid_lat = 0
        self._last_valid_alt = 0

    def __write_reg(self, reg, data) -> None:
        """
        Write data to the I2C register
        :param reg: register address
        :param data: data to write
        :return: None
        """
        if isinstance(data, int):
            data = [data]

        self.__i2c.writeto_mem(self.__addr, reg, bytearray(data))

    def __read_reg(self, reg, length) -> bytes:
        """
        Reads data from the I2C register
        :param reg: I2C register address
        :param length: number of bytes to read
        :return: bytes
        """
        try:
            result = self.__i2c.readfrom_mem(self.__addr, reg, length)
        except OSError:
            return None

        return result

    @staticmethod
    def __calculate_latitude_longitude(value: bytes) -> float:
        """
        Calculates the latitude and longitude from bytes to float
        :param value: gnss value in bytes
        :return: list
        """
        val_dd = value[0]
        val_mm = value[1]
        val_mm_mm = value[2] * 65536 + value[3] * 256 + value[4]
        degree = val_dd + val_mm / 60.0 + val_mm_mm / 100000.0 / 60.0

        return degree

    @staticmethod
    def __optional_calculate_bytes_to_float(value: bytes) -> float:
        """
        Calculates the bytes to float (for altitude, cog and sog)
        :param value: gnss bytes
        :return: float
        """
        return value[0] * 256 + value[1] + value[2] / 100.0

    def set_enable_power(self) -> None:
        """
        Enable gnss power
        :return: None
        """
        self.__write_reg(self.I2C_SLEEP_MODE, self.ENABLE_POWER)
        sleep_ms(100)

    def set_disable_power(self) -> None:
        """
        Disable gnss power
        :return: None
        """
        self.__write_reg(self.I2C_SLEEP_MODE, self.DISABLE_POWER)
        sleep_ms(100)

    def set_gnss_mode(self, mode: int) -> None:
        """
        Set gnss mode
        - 1 for GPS
        - 2 for BeiDou
        - 3 for GPS + BeiDou
        - 4 for GLONASS
        - 5 for GPS + GLONASS
        - 6 for BeiDou + GLONASS
        - 7 for GPS + BeiDou + GLONASS
        :param mode: number for mode
        :return: None
        """
        if 1 <= mode <= 7:
            self.__write_reg(self.I2C_GNSS_MODE, int(mode))
            sleep_ms(100)

    def get_gnss_mode(self) -> int:
        """
        Get gnss mode (1 till 7)
        :return: number for GNSS mode
        """
        result = self.__read_reg(self.I2C_GNSS_MODE, 1)
        return int(result[0])

    def get_num_sta_used(self) -> int:
        """
        Get number of current satellite used
        :return: number of current satellite used
        """
        result = self.__read_reg(self.I2C_USE_STAR, 1)
        return int(result[0])

    def get_time(self):
        """
        Get utc time and return in format HH MM SS
        :return: int,int,int
        """
        result = self.__read_reg(self.I2C_HOUR, 3)

        if result:
            hour = result[0] + 2
            minute = result[1]
            second = result[2]
        else:
            hour = 0
            minute = 0
            second = 0

        return hour,minute,second

    def get_lat(self) -> float:
        """
        Get latitude and return in format degree
        :return: float
        """
        result = self.__read_reg(self.I2C_LAT_1, 6)
        res_lon = self.__read_reg(self.I2C_LON_1, 6)
        direction = 'S'

        if result and res_lon:
            degree = DFR_GNSS_I2C.__calculate_latitude_longitude(result)

            if len(res_lon) >= 5:
                direction = chr(res_lon[5])

            if direction == 'S':
                degree = -degree
        else:
            degree = self._last_valid_lat

        self._last_valid_lat = degree
        return degree

    def get_lon(self) -> float:
        """
        Get longitude and return in format degree
        :return: float
        """
        result = self.__read_reg(self.I2C_LON_1, 6)
        res_lat = self.__read_reg(self.I2C_LAT_1, 6)
        direction = "W"

        if result and res_lat:
            degree = DFR_GNSS_I2C.__calculate_latitude_longitude(result)

            if len(res_lat) >= 5:
                direction = chr(res_lat[5])

            if direction == 'W':
                degree = -degree

        else:
            degree = self._last_valid_lon

        self._last_valid_lon = degree
        return degree

    def get_alt(self) -> float:
        """
        Get altitude over ground in meters
        :return: float
        """
        result = self.__read_reg(self.I2C_ALT_H, 3)

        if result:
            high = DFR_GNSS_I2C.__optional_calculate_bytes_to_float(result)
        else:
            high = self._last_valid_alt

        self._last_valid_alt = high

        return high

    def get_position(self) -> list:
        """
        Renvoie et affiche les différentes valeurs récupérable par le GPS
        """
        lat = self.get_lat()
        lon = self.get_lon()
        alt = self.get_alt()
        heures, minutes, secondes = self.get_time()
        return [lat, lon, alt, heures, minutes, secondes]
