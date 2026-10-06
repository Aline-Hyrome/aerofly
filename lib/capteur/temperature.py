from .capteur import Capteur


class Temperature(Capteur):
    def get(self) -> list[int]:
        return self.__capteur.temperature()

    def key(self):
        return "Temperature"
