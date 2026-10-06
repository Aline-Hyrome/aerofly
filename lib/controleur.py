from time import sleep, time

from assistance import Assistance
from capteur import IMU, GPS, PressionDiff, Pression, Vitesse, BMS, Humidite, Temperature
from composant import DFR_GNSS_I2C, BNO055, SEN0343, INA3221, SHT3X
from communication import IBUS, CommunicationLoRa
from moteur import MoteurHelice, ServoMoteur
from busI2C import BusI2C
import pycom


class Controleur:
    """Classe principal du projet AEROFLY
    """
    def __init__(self, config: dict) -> None:
        """Constructeur de la classe Controleur

        :param config: Configuration de tout les composants doit être une copie de configuration.json
        :type config: dict
        """
        self._debug = config["debug"]

        self.__log("Initialisation Controleur")

        self.__rafraichissement = config["controleur"]["rafraichissement_seconde"]
        self.__rafraichissement_lora = config["controleur"]["rafraichissement_lora_seconde"]

        self.__log("Initialisation CommunicationLoRa")
        self.__lora = CommunicationLoRa(**config["communication"]["lora"], debug=self._debug)

        self.__log("Initialisation IBUS")
        self.__ibus = IBUS(1, **config["communication"]["ibus"])

        self.__log("Initialisation Moteurs")
        self.__moteur_gaz = MoteurHelice(**config["moteur"]["moteur_gaz"])
        self.__servo_profondeur = ServoMoteur(**config["moteur"]["servo_profondeur"])
        self.__servo_ailerons1 = ServoMoteur(**config["moteur"]["servo_ailerons1"])
        self.__servo_ailerons2 = ServoMoteur(**config["moteur"]["servo_ailerons2"])
        self.__servo_direction = ServoMoteur(**config["moteur"]["servo_direction"])

        self.__servo_profondeur.set_rapport_cyclique_ajuste(0)
        self.__servo_profondeur.set_rapport_cyclique_ajuste(0.5)
        self.__servo_ailerons1.set_rapport_cyclique_ajuste(0.5)
        self.__servo_ailerons2.set_rapport_cyclique_ajuste(0.5)
        self.__servo_direction.set_rapport_cyclique_ajuste(0.5)

        self.__log("Initialisation Assistance")
        self.__assistance = Assistance(config["moteur"], config["assistance"], self.__rafraichissement)

        self.__flag = True

        self.__liste_capteur = []

        self.__mesures = {
            "Temperature": 0,
            "Pression": 0,
            "Humidite": 0,
            "Vitesse": 0,
            "Tension": 0,
            "Orientation": [0, 0, 0],
            "GPS": [0, 0, 0, 0, 0, 0],
        }

        self.__log("Initialisation Bus I2C")
        bus_i2c_IMU = BusI2C(0, **config["communication"]["bus_i2c_IMU"]).i2c_bus
        bus_i2c_fast = BusI2C(1, **config["communication"]["bus_i2c_fast"]).i2c_bus

        self.__log("Initialisation BNO055")
        adresse_BNO055 = config["composant"]["BNO055"]["adresse_i2c_decimal"]
        try:
            self.__imu = IMU(BNO055(adresse_BNO055, bus_i2c_IMU))
            self.__liste_capteur.append(self.__imu)
        except OSError as e:
            self.__log("IMU ne répond pas. %s" %e)
        except RuntimeError as e:
            self.__log("IMU ne répond pas. %s" %e)

        self.__log("Initialisation GPS")
        adresse_GPS = config["composant"]["DFR_GNSS_GPS"]["adresse_i2c_decimal"]
        try:
            gps = GPS(DFR_GNSS_I2C(bus_i2c_fast, adresse_GPS))
            self.__liste_capteur.append(gps)
        except OSError as e:
            self.__log("GPS ne répond pas. %s" %e)

        self.__log("Initialisation Sonde Pitot")
        adresse_pitot = config["composant"]["SEN0343"]["adresse_i2c_decimal"]
        try:
            vitesse = Vitesse(SEN0343(bus_i2c_fast, adresse_pitot))
            self.__liste_capteur.append(vitesse)
        except OSError as e:
            self.__log("Sonde Pitot ne répond pas. %s" %e)

        self.__log("Initialisation BMS")
        adresse_BMS = config["composant"]["INA3221"]["adresse_i2c_decimal"]
        try:
            bms = BMS(INA3221(bus_i2c_fast, adresse_BMS))
            self.__liste_capteur.append(bms)
        except OSError as e:
            self.__log("BMS ne répond pas. %s" %e)

        self.__log("Initialisation SHT3X")
        adresse_SHT3X = config["composant"]["SHT3X"]["adresse_i2c_decimal"]
        try:
            sht3x = SHT3X(bus_i2c_fast, adresse_SHT3X)
            humidite = Humidite(sht3x)
            self.__liste_capteur.append(humidite)

            temperature = Temperature(sht3x)
            self.__liste_capteur.append(temperature)
        except OSError as e:
            self.__log("SHT3X ne répond pas. %s" %e)

    def __log(self, message: str) -> None:
        """Méthode de logging

        :param message: message de log
        :type message: str
        """
        if self._debug:
            print(message)

    @property
    def flag(self) -> bool:
        """ getter de la variable permettant d'activer / Désactiver le boucle principale

        :return: boolean
        :rtype: bool
        """
        return self.flag

    @flag.setter
    def flag(self, value: bool) -> None:
        """ Permet d'activer / Désactiver le boucle principale

        :param value: boolean
        :type value: bool
        """
        if isinstance(value, bool):
            self.__flag = value

    def __get_envoi_mesures(self) -> None:
        """ Permet de récupérer toutes les données des composants et les envoies sur le réseau LoRaWAN
        """
        # Chaque appel de composant dure ~ 10ms 
        # A 5 composants la durée d'une itération de la boucle principal double si rafraichissement = 0.05
        # L'usage d'un thread n'est pas permise.
        # Lors d'un usage de lora dans un thread crash le système.
        for capteur in self.__liste_capteur:
            try:
                self.__mesures[capteur.key()] = capteur.get()
            except:
                pass
        self.__lora.communiquer(self.__mesures)

    def mainloop(self) -> None:
        """Boucle principale
        """
        self.__log("Démarrage mainloop")

        start_time = time()
        start_ledtime = time()

        while self.__flag:
            self.__ibus.decode2()
            if hasattr(self, "__imu"):
                yaw, roll, pitch = self.__imu.get()
            else:
                yaw, roll, pitch = (None, None, None)
            self.__log("y: %s, r: %s, p: %s" %(yaw, roll, pitch))

            if self.__assistance.boolean():
                self.__ibus.ch3 = self.__assistance.rectifier_gaz(self.__ibus.ch3)
                self.__ibus.ch2 = self.__assistance.rectifier_profondeur(self.__ibus.ch2, pitch)
                self.__ibus.ch1 = self.__assistance.rectifier_ailerons(self.__ibus.ch1, roll)
                self.__ibus.ch4 = self.__assistance.rectifier_direction(self.__ibus.ch4)

            self.__moteur_gaz.set_duree_etat_actif(self.__ibus.ch3)
            self.__servo_profondeur.set_duree_etat_actif(self.__ibus.ch2)
            self.__servo_ailerons1.set_duree_etat_actif(self.__ibus.ch1)
            self.__servo_ailerons2.set_duree_etat_actif(self.__ibus.ch1)
            self.__servo_direction.set_duree_etat_actif(self.__ibus.ch4)
            self.__assistance.assistance_flat = self.__ibus.ch5
            self.__assistance.assistance_dynamique = self.__ibus.ch6

            if (time() - start_time) >= self.__rafraichissement_lora:
                self.__get_envoi_mesures()
                start_time = time()

            if time() - start_ledtime >= 2:
                pycom.rgbled(0x00FF00)
                start_ledtime = time()
            else:
                pycom.rgbled(0x000000)

            sleep(self.__rafraichissement)
