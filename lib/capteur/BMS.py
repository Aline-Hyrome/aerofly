from .capteur import Capteur


class BMS(Capteur):
    """Classe BMS
    """

    def get(self) -> float:
        self.__capteur.main_tension()
        return self.__capteur.get_canal1()[0]

    def key(self):
        return "Tension"