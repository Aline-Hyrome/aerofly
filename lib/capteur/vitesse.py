from .capteur import Capteur


class Vitesse(Capteur):
    """Classe Vitesse
    """
    def get(self) -> float:
        return self.__capteur.get_speed()

    def key(self):
        return "Vitesse"