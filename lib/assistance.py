from capteur import Accelerometre, Capteur, Gyroscope
from communication import IBUS

class Assistance:

    def __init__(self, gyroscope: Gyroscope, accelerometre: Accelerometre, etat_actif_min, etat_actif_max):
        self.__gyroscope = gyroscope
        self.__accelerometre = accelerometre
        self.__rectification = 0 #200 * 10 ** (-6)
        self.__etat_actif_min = etat_actif_min
        self.__etat_actif_max = etat_actif_max
        print(etat_actif_min)
        print(etat_actif_max)
        self.__min_rectification = self.__etat_actif_min + self.__rectification
        self.__max_rectification = self.__etat_actif_max - self.__rectification
        print(self.__min_rectification)
        print(self.__max_rectification)

    @property
    def rectification(self):
        return self.__rectification

    @rectification.setter
    def rectification(self, nouvelle_valeur: float):
        # Si la nouvelle valeur est superieure à la différence entre la moyenne de l'intervalle et le minimum alors nous réattribuons pas
        # Avec min = 1000 et max = 2000
        # moyenne = 1500
        # si la nouvelle valeur est au dessus de 500 alors pas de réattribution
        if nouvelle_valeur < ((self.__etat_actif_min + self.__etat_actif_max) / 2) - self.__etat_actif_min:
            self.__rectification = nouvelle_valeur

    def __rectifier_flat(self, valeur: float) -> float:
        print("av flat", valeur)
        print("ap flat", self.__min_rectification + ((valeur - self.__etat_actif_min) * (self.__max_rectification - self.__min_rectification)) / (self.__etat_actif_max - self.__etat_actif_min))
        return self.__min_rectification + ((valeur - self.__etat_actif_min) * (self.__max_rectification - self.__min_rectification)) / (self.__etat_actif_max - self.__etat_actif_min)

    def rectifier_gaz(self, valeur: float) -> float:
        if self.__rectification:
            valeur = self.__rectifier_flat(valeur)
        return valeur

    def rectifier_ailerons(self, valeur: float) -> float:
        if self.__rectification:
            valeur = self.__rectifier_flat(valeur)
        return valeur

    def rectifier_direction(self, valeur: float) -> float:
        if self.__rectification:
            valeur = self.__rectifier_flat(valeur)
        return valeur

    def rectifier_profondeur(self, valeur: float) -> float:
        if self.__rectification:
            valeur = self.__rectifier_flat(valeur)
        return valeur

    def __bool__(self):
        if self.__rectification:
            return True
        else:
            return False