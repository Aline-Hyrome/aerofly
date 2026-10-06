from .moteur import Moteur
from machine import PWM
from time import sleep

class ServoMoteur(Moteur):
    """Classe définissant les servomoteurs PWM
    """

    def __init__(self, pin: int, frequence: int, etat_actif_min: int, etat_actif_max: int) -> None:
        """Instancie un ServoMoteur.

        :param pin: Le pin DATA du servomoteur
        :type pin: int
        :param frequence: Fréquence PWM en Hz
        :type frequence: int
        :param min_pulse: Durée de l'état actif minimum en secondes
        :type min_pulse: int
        :param max_pulse: Durée de l'état actif maximum en secondes
        :type max_pulse: int
        """
        super().__init__(pin, frequence, etat_actif_min, etat_actif_max)

    def set_duree_etat_actif(self, duree_etat_actif: float) -> None:
        """Méthode permettant de modifier l'angle du servomoteur via
        une valeur float, de valeurs entre min_etat_actif à max_etat_actif
        :param duree_etat_actif: Durée de l'état actif maximum en secondes
        :type duree_etat_actif: float
        """
        if (duree_etat_actif < self.__etat_actif_min or duree_etat_actif > self.__etat_actif_max):
            raise ValueError("""Impossible de modifier l'état le rapport cyclique doit être entre %s et %s \
            Valeur: %s""" %(self.__etat_actif_min, self.__etat_actif_max, duree_etat_actif))

        self.pwm_c.duty_cycle(duree_etat_actif/self.periode)

    def set_rapport_cyclique_ajuste(self, rapport_cyclique: float) -> None:
        """Méthode permettant de modifier l'état du servomoteur
        avec une valeur entre 0 et 1
        0 étant sa valeur d'angle minimal
        1 étant sa valeur d'angle maximal
        :param duree_etat_actif: Rapport cyclique en 0 et 1
        :type duree_etat_actif: float
        """
        rapport_cyclique_ajuste = (self.__etat_actif_min*(1-rapport_cyclique)+self.__etat_actif_max*(0+rapport_cyclique))*100
        self.pwm_c.duty_cycle(rapport_cyclique_ajuste)
