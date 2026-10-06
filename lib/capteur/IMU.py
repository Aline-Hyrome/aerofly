from .capteur import Capteur


class IMU(Capteur):
    """Classe IMU
    """
    def get(self) -> list[float]:
        return self.__capteur.euler()

    def key(self):
        return "Orientation"