from .capteur import Capteur
from busI2C import BusI2C
from composant import Composant

class Accelerometre(Capteur):
    def __init__(self, capteur: Composant) -> None:
        self.__capteur = capteur

    def get(self) -> list[int]:
        return self.__capteur.get_accelerometre()