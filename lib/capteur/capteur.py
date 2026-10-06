from abc import ABC, abstractmethod

class Capteur(ABC):
    @abstractmethod
    def get(self):
        """Cette méthode est appellée afin d'obtenir les données
        du capteur en question
        """
        pass
