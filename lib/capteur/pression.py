from .capteur import Capteur


class Pression(Capteur):
    """Classe Pression
    """
    def get(self) -> int:
        return self.__capteur.get()

    def key(self):
        return "Pression"