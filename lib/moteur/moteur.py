from abc import ABC, abstractmethod
from machine import PWM
from time import sleep

class Moteur(ABC):
    """Classe abstraite définissant les moteurs PWM
    """
    __pin_utilise = []
    # id permet de sélectionner l'id du channel PWM
    __id = 0

    def __init__(self, pin: int, frequence: int, etat_actif_min: int, etat_actif_max: int) -> None:
        # Vérification du pin
        # Les pins disponible pour le PWM sur un lopy4 sont de 0 à 12 et de 19 à 23
        if pin < 0 or pin > 23 or (pin > 12 and pin < 19):
            raise ValueError("Le pin %s n'est pas sur un pin disponible pour le PWM" %pin)

        if pin in Moteur.__pin_utilise:
            raise ValueError("Le pin %s est déjà utilisé!" %pin)

        self.__etat_actif_min = etat_actif_min
        self.__etat_actif_max = etat_actif_max
        self._frequence = frequence
        self.__periode = 1/self._frequence
        self.__pwm = PWM(0, self._frequence)
        self.__pin = "P" + str(pin)
        self.pwm_c = self.__pwm.channel(Moteur.__id, pin=self.__pin)
        Moteur.__id += 1
        Moteur.__ajouter_pin(self.__pin)

    @classmethod
    def __ajouter_pin(cls, pin: str) -> None:
        Moteur.__pin_utilise.append(pin)

    @classmethod
    def __enlever_pin(cls, pin: str) -> None:
        Moteur.__pin_utilise.remove(pin)

    def __del__(self) -> None:
        try:
            Moteur.__enlever_pin(self.__pin)
        except AttributeError:
            pass

    def calibration(self):
        """Séquence d'initialisation d'un servomoteur.
        Cette séquence à pour but d'envoyer une confirmation visuelle
        que le servomoteur fonctionne lors du démarrage.
        """
        self.set_rapport_cyclique_ajuste(0)
        sleep(1)
        self.set_rapport_cyclique_ajuste(1)
        sleep(1)
        self.set_rapport_cyclique_ajuste(0.5)
        sleep(1)

    @property
    def periode(self):
        return self.__periode

    @property
    def pin(self):
        return self.__pin

    @abstractmethod
    def set_duree_etat_actif(self, duree_etat_actif: float) -> None:
        """Méthode permettant de modifier l'état du servomoteur
        """
        pass

    @abstractmethod
    def set_rapport_cyclique_ajuste(self, rapport_cyclique: float) -> None:
        """Méthode permettant de modifier l'état du servomoteur
        """
        pass
