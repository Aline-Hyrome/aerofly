from abc import ABC, abstractmethod
from composant import Composant


class Capteur(ABC):
    def __init__(self, capteur: Composant) -> None:
        """ Constructeur des classes capteur

        :param capteur: driver du composant
        :type capteur: Composant
        """
        self.__capteur = capteur

    @abstractmethod
    def get(self) -> float | list[float]:
        """Cette méthode est appellée afin d'obtenir les données
        du capteur
        """
        pass

    @abstractmethod
    def key(self) -> str:
        """Cette méthode est appellée afin d'obtenir le nom de la clé
        correspondante au capteur
        Notamment utilise pour faire des mesures
        """
        pass
