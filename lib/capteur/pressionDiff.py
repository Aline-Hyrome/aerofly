from .capteur import Capteur


class PressionDiff(Capteur):
    """Classe Pression Différentielle
    """
    def get(self) -> float:
        return self.__capteur.get_data()[0]

    def key(self):
        return "Pression_differentielle"
