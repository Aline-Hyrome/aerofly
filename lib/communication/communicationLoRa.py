from network import LoRa
import socket
import ubinascii
import ustruct


class CommunicationLoRa:
    """
    Classe qui gère toutes les communications LoRa.
    """

    __ordre_fixe = [
        "GPS",
        "Orientation",
        "Pression",
        "Temperature",
        "Humidite",
        "Tension",
        "Vitesse"
    ]

    def __init__(self, app_eui: str, app_key: str, debug=False):
        """Point d'entrée"""
        self._debug = debug
        self.__APP_EUI = app_eui
        self.__APP_KEY = app_key
        self.__DEV_EUI = LoRa().mac()
        self.__log("dev_eui: %s" %self.__DEV_EUI)
        self.__lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
        self.socket = self.creer_socket()
        self.__joindre()
        self.__log("Liaison etablie.")

    def __log(self, message: str):
        if self._debug:
            print(message)

    def message(self, dico={}):
        """
        Renvoie les mesures faites par les différents composants en hexadécimal.
        """
        trame = b""
        for k in self.__ordre_fixe:
            try:
                v = dico[k]
            except KeyError as e:
                self.__log("Error on:", e)
                continue
            if k in ["GPS"]:
                for elem in v:
                    if isinstance(elem, float):
                        trame += ustruct.pack('>f', elem)
                    else:
                        trame += ustruct.pack('>B', elem)
            elif k in ["Orientation"]:
                for elem in v:
                    trame += ustruct.pack('>f', elem)
            elif k in ["Vitesse", "Tension", "Temperature", "Humidite"]:
                trame += ustruct.pack('>f',v)
            elif k in ["Pression"]:
                trame += ustruct.pack('>H', int(v))
        return trame

    def __joindre(self):
        """
        Joint la passerelle LoRa.
        """
        app_eui = ubinascii.unhexlify(self.__APP_EUI)
        app_key = ubinascii.unhexlify(self.__APP_KEY)
        dev_eui = self.__DEV_EUI
        for i in range(2):
            try:
                self.__lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=10000)
                break
            except OSError:
                self.__log("Lora joined: %s" %self.__lora.has_joined())
                continue

    def creer_socket(self):
        """
        Crée une socket.
        """
        socket_lora = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        socket_lora.setsockopt(socket.SOL_LORA, socket.SO_DR, 6)
        socket_lora.setblocking(False)
        return socket_lora

    def communiquer(self, dico={}):
        """
        Boucle de communication LoRa.
        """
        if self.__lora.has_joined():
            self.__log("Creating frame %s" %dico)
            trame = self.message(dico)
            self.socket.send(trame)
            self.__lora.nvram_save()
            self.__log("Sending: %s)" %ubinascii.hexlify(trame).decode('utf-8'))

