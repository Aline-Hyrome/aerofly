class IBUS:
    """Classe qui gère toutes les communications via IBUS
    """
    # 0x20 0x40
    BHEADER = b" @"
    __FLUSH_INTERVAL = 3

    def __init__(self, bus, baudrate, pins, timeout_chars) -> None:
        """Point d'entrée
        """
        self.__bus = bus
        #self.__bus.init(baudrate=baudrate, pins=pins, timeout_chars=timeout_chars)
        self.__etat_actif_min = 500 * 10 **(-6)
        self.__etat_actif_max = 2500 * 10 **(-6)
        # Jusqu'a 14 canaux
        self.__ch1 = 1500 * 10 **(-6)# 1500 ou b"\xdc\x05"
        self.__ch2 = 1500 * 10 **(-6)
        self.__ch3 = 1500 * 10 **(-6)
        self.__ch4 = 1500 * 10 **(-6)
        self.__ch5 = 1500 * 10 **(-6)
        self.__ch6 = 1500 * 10 **(-6)

        self.__counter = 0

    def bytes_to_int(self, octets: bytes) -> int:
        """Convertie des octets little endian en entier

        :param octets: octet(s) little endian
        :type octets: bytes
        :return: Valeur converti en entier
        :rtype: int
        """
        return int.from_bytes(octets, "little")

    def decode2(self) -> None:
        """
        Permet le rafraichissement des données des canaux
        """
        header = self.__bus.read(2)
        data = self.__bus.read(30)
        # Le buffer se remplit rapidement la fréquence du récepteur est d'environ 100Hz
        # Le fréquence de rafraichissement de la classe contrôleur est de 20Hz
        # Le buffer se remplit donc 5x plus rapidement qu'il ne se vide
        # Le buffer peut contenir 512 octets
        # Par conséquent toutes les 3 itérations du contrôleur le buffer sera pratiquement rempli
        # 3 itération = 15 trames ; 512 octets = 16 trames
        # On est obligé de vider le buffer
        if self.__counter % self.__FLUSH_INTERVAL == 2:
            self.__flush_buffer()

        if header == IBUS.BHEADER:
            self.__ch1 = self.bytes_to_int(data[0:2]) * 10**(-6)
            self.__ch2 = self.bytes_to_int(data[2:4]) * 10**(-6)
            self.__ch3 = self.bytes_to_int(data[4:6]) * 10**(-6)
            self.__ch4 = self.bytes_to_int(data[6:8]) * 10**(-6)
            self.__ch5 = self.bytes_to_int(data[8:10]) * 10**(-6)
            self.__ch6 = self.bytes_to_int(data[10:12]) * 10**(-6)

        self.__counter += 1

    def __flush_buffer(self) -> None:
        """ Vide completement le buffer UART
        """
        self.__bus.read(self.__bus.any())

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
