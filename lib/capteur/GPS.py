from .capteur import Capteur


class GPS(Capteur):
    """Classe GPS
    """
    def get(self) -> list[float]:
        return self.__capteur.get_position()

    def key(self):
        return "GPS"