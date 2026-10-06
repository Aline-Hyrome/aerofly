from machine import UART
from time import sleep
import ubinascii
import _thread

class IBUS(UART):
    """Classe qui gère toutes les communications via IBUS
    """
    BHEADER = b" @"

    def __init__(self, bus, baudrate, pins, timeout_chars) -> None:
        """Point d'entrée
        """
        self.init(baudrate=baudrate, pins=pins, timeout_chars=timeout_chars)
        self.__index = 0
        self.__etat_actif_min = 1000 * 10 **(-6)
        self.__etat_actif_max = 2000 * 10 **(-6)
        self.__ch1 = 1500 * 10 **(-6)# 1500 ou b"\xdc\x05"
        self.__ch2 = 1500 * 10 **(-6)
        self.__ch3 = 1500 * 10 **(-6)
        self.__ch4 = 1500 * 10 **(-6)
        self.__ch5 = 1500 * 10 **(-6)
        self.__ch6 = 1500 * 10 **(-6)
        self.__ch7 = 1500 * 10 **(-6)

    def bytes_to_int(self, octets: bytes) -> int:
        return int.from_bytes(octets, "little")

    def decode2(self) -> None:
        """
        Permet le rafraichissement des données des canaux
        """
        self.read(self.__index)
        header = self.read(2)
        data = self.read(30)
        self.__flush_buffer()
        if header == IBUS.BHEADER:
            self.__ch1 = self.bytes_to_int(data[0:2]) * 10**(-6)
            self.__ch2 = self.bytes_to_int(data[2:4]) * 10**(-6)
            self.__ch3 = self.bytes_to_int(data[4:6]) * 10**(-6)
            self.__ch4 = self.bytes_to_int(data[6:8]) * 10**(-6)
            self.__ch5 = self.bytes_to_int(data[8:10]) * 10**(-6)
            self.__ch6 = self.bytes_to_int(data[10:12]) * 10**(-6)
        elif data is not None:
            self.__index = data.find(IBUS.BHEADER)

    def __flush_buffer(self) -> None:
        self.read(self.any())

    @property
    def ch1(self) -> float:
        """Retourne la valeur pour le canal 1

        :return: Valeur canal 1
        :rtype: float
        """
        return self.__ch1
    
    @ch1.setter
    def ch1(self, nouvelle_valeur: float):
        if nouvelle_valeur >= self.__etat_actif_min or nouvelle_valeur <= self.__etat_actif_max:
            self.__ch1 = nouvelle_valeur

    @property
    def ch2(self) -> float:
        """Retourne la valeur pour le canal 2

        :return: Valeur canal 2
        :rtype: float
        """
        return self.__ch2

    @ch2.setter
    def ch2(self, nouvelle_valeur: float):
        if nouvelle_valeur >= self.__etat_actif_min or nouvelle_valeur <= self.__etat_actif_max:
            self.__ch2 = nouvelle_valeur

    @property
    def ch3(self) -> float:
        """Retourne la valeur pour le canal 3

        :return: Valeur canal 3
        :rtype: float
        """
        return self.__ch3
    
    @ch3.setter
    def ch3(self, nouvelle_valeur: float):
        if nouvelle_valeur >= self.__etat_actif_min or nouvelle_valeur <= self.__etat_actif_max:
            self.__ch3 = nouvelle_valeur

    @property
    def ch4(self) -> float:
        """Retourne la valeur pour le canal 4

        :return: Valeur canal 4
        :rtype: float
        """
        return self.__ch4

    @ch4.setter
    def ch4(self, nouvelle_valeur: float):
        if nouvelle_valeur >= self.__etat_actif_min or nouvelle_valeur <= self.__etat_actif_max:
            self.__ch4 = nouvelle_valeur

    @property
    def ch5(self) -> float:
        """Retourne la valeur pour le canal 5

        :return: Valeur canal 5
        :rtype: float
        """
        return self.__ch5

    @ch5.setter
    def ch5(self, nouvelle_valeur: float):
        if nouvelle_valeur >= self.__etat_actif_min or nouvelle_valeur <= self.__etat_actif_max:
            self.__ch5 = nouvelle_valeur

    @property
    def ch6(self) -> float:
        """Retourne la valeur pour le canal 6

        :return: Valeur canal 6
        :rtype: float
        """
        return self.__ch6

    @ch6.setter
    def ch6(self, nouvelle_valeur: float):
        if nouvelle_valeur >= self.__etat_actif_min or nouvelle_valeur <= self.__etat_actif_max:
            self.__ch6 = nouvelle_valeur
