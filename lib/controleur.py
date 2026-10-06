from moteur import ServoMoteur
from communication import IBUS
from time import sleep
from assistance import Assistance

class Controleur:

    RAFRAICHISSEMENT = 0.05

    def __init__(self, assistance: Assistance, etat_actif_min: int, etat_actif_max: int) -> None:
        self.__servo_gaz = ServoMoteur(23, 100, etat_actif_min, etat_actif_max)
        self.__servo_profondeur = ServoMoteur(22, 100, etat_actif_min, etat_actif_max)
        self.__servo_ailerons = ServoMoteur(21, 100, etat_actif_min, etat_actif_max)
        self.__servo_direction = ServoMoteur(20, 100, etat_actif_min, etat_actif_max)

        self.__ibus = IBUS(1, 115200, pins=('P3','P4'), timeout_chars=10)
        self.__assistance = assistance

        # self.__servo_gaz.calibration()
        # self.__servo_profondeur.calibration()
        # self.__servo_ailerons.calibration()
        # self.__servo_direction.calibration()
        self.flag = True

    def mainloop(self) -> None:
        while self.flag:
            self.__ibus.decode2()

            if self.__assistance:
                print("av", self.__ibus.ch3)
                self.__ibus.ch3 = self.__assistance.rectifier_gaz(self.__ibus.ch3)
                print("ap", self.__ibus.ch3)
                self.__ibus.ch2 = self.__assistance.rectifier_profondeur(self.__ibus.ch2)
                self.__ibus.ch4 = self.__assistance.rectifier_ailerons(self.__ibus.ch4)
                self.__ibus.ch1 = self.__assistance.rectifier_direction(self.__ibus.ch1)

            self.__servo_gaz.set_duree_etat_actif(self.__ibus.ch3)
            self.__servo_profondeur.set_duree_etat_actif(self.__ibus.ch2)
            self.__servo_ailerons.set_duree_etat_actif(self.__ibus.ch4)
            self.__servo_direction.set_duree_etat_actif(self.__ibus.ch1)
            sleep(Controleur.RAFRAICHISSEMENT)