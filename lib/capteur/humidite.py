from .capteur import Capteur


class Humidite(Capteur):
    def get(self) -> list[int]:
        return self.__capteur.humidite()

    def key(self):
        return "Humidite"