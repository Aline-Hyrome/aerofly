from PID import PID
from utime import ticks_ms

class Assistance:
    """La classe Assistance
    """
    def __init__(self, config_moteur: dict, config_assistance: dict, dt: float) -> None:
        """Constructeur Assistance

        :param config_moteur: Configuration Totale des moteurs référence dans le fichier de configuration
        :type config_moteur: dict
        :param config_assistance: Configuration de l'assistance référence dans le fichier de configuration
        :type config_assistance: dict
        :param dt: Durée en seconde entre chaque appel des pids, doit être la valeur de rafraichissment du contrôleur
        :type dt: float
        """
        self.__assistance_flat_dynamique = config_assistance["rectification_fixe_etat_actif_mid_air"]
        self.__assistance_dynamique_PID_range = config_assistance["rectification_dynamique_etat_actif_range_from_middle"]
        self.__assistance_flat = False
        self.__assistance_dynamique = False

        self.__end_PID_profondeur = True
        self.__end_PID_ailerons = True

        self.__middle_point_ailerons = (config_moteur["servo_ailerons1"]["etat_actif_min"] + config_moteur["servo_ailerons1"]["etat_actif_max"]) / 2
        self.__middle_point_profondeur = (config_moteur["servo_profondeur"]["etat_actif_min"] + config_moteur["servo_profondeur"]["etat_actif_max"]) / 2

        self.__ailerons_PID = PID(config_assistance["Kp_ailerons"], config_assistance["Ki_ailerons"], config_assistance["Kp_ailerons"], setpoint=0, sample_time=dt*1000, time_fn=ticks_ms)
        self.__profondeur_PID = PID(config_assistance["Kp_profondeur"], config_assistance["Ki_profondeur"], config_assistance["Kp_profondeur"], setpoint=0, sample_time=dt*1000, time_fn=ticks_ms)
        self.__ailerons_PID.output_limits = (config_moteur["servo_ailerons1"]["angle_min"], config_moteur["servo_ailerons1"]["angle_max"])
        self.__profondeur_PID.output_limits = (config_moteur["servo_profondeur"]["angle_min"], config_moteur["servo_profondeur"]["angle_max"])

        self.__config_gaz = config_moteur["moteur_gaz"]
        self.__config_gaz["rectification_fixe_etat_actif"] = config_assistance["rectification_fixe_etat_actif_gaz"]
        self.__config_gaz["min_rectification"] = self.__config_gaz["etat_actif_min"] + self.__config_gaz["rectification_fixe_etat_actif"]
        self.__config_gaz["max_rectification"] = self.__config_gaz["etat_actif_max"] - self.__config_gaz["rectification_fixe_etat_actif"]

        self.__config_profondeur = config_moteur["servo_profondeur"]
        self.__config_profondeur["rectification_fixe_etat_actif"] = config_assistance["rectification_fixe_etat_actif_profondeur"]
        self.__config_profondeur["min_rectification"] = self.__config_profondeur["etat_actif_min"] + self.__config_profondeur["rectification_fixe_etat_actif"]
        self.__config_profondeur["max_rectification"] = self.__config_profondeur["etat_actif_max"] - self.__config_profondeur["rectification_fixe_etat_actif"]

        self.__config_ailerons = config_moteur["servo_ailerons1"]
        self.__config_ailerons["rectification_fixe_etat_actif"] = config_assistance["rectification_fixe_etat_actif_ailerons"]
        self.__config_ailerons["min_rectification"] = self.__config_ailerons["etat_actif_min"] + self.__config_ailerons["rectification_fixe_etat_actif"]
        self.__config_ailerons["max_rectification"] = self.__config_ailerons["etat_actif_max"] - self.__config_ailerons["rectification_fixe_etat_actif"]

        self.__config_direction = config_moteur["servo_direction"]
        self.__config_direction["rectification_fixe_etat_actif"] = config_assistance["rectification_fixe_etat_actif_direction"]
        self.__config_direction["min_rectification"] = self.__config_direction["etat_actif_min"] + self.__config_direction["rectification_fixe_etat_actif"]
        self.__config_direction["max_rectification"] = self.__config_direction["etat_actif_max"] - self.__config_direction["rectification_fixe_etat_actif"]

    def map(self, value, in_min, in_max, out_min, out_max):
        """ Convertie une valeur située entre deux borne en une valeur proportionnel entre deux autres limites

        :param value: Valeur à convertir
        :type value: float
        :param in_min: Limite inférieure entrante
        :type in_min: float
        :param in_max: Limite supérieure entrante
        :type in_max: float
        :param out_min: Limite inférieure Sortante
        :type out_min: float
        :param out_max: Limite supérieure Sortante
        :type out_max: float
        :return: Valeur proportionnel convertie
        :rtype: float
        """
        return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def __rectifier_flat(self, valeur: float, config: dict) -> float:
        """ Rectifie une durée à l'état haut PWM

        :param valeur: Valeur PWM
        :type valeur: float
        :param config: configuration de la commande émettrice
        :type config: dict
        :return: Valeur PWM rectifiée
        :rtype: float
        """
        if self.__assistance_flat_dynamique:
            offset = self.map(self.__assistance_flat, config["etat_actif_min"] * 10 ** (-6), config["etat_actif_max"] * 10 ** (-6), 0, config["rectification_fixe_etat_actif"])
            min_rectification = config["etat_actif_min"] + offset
            max_rectification = config["etat_actif_max"] - offset
            valeur = min_rectification + ((valeur - config["etat_actif_min"]) * (max_rectification - min_rectification)) / (config["etat_actif_max"] - config["etat_actif_min"])
        else:
            valeur = config["min_rectification"] + ((valeur - config["etat_actif_min"]) * (config["max_rectification"] - config["min_rectification"])) / (config["etat_actif_max"] - config["etat_actif_min"])
        return valeur

    def rectifier_gaz(self, valeur: float) -> float:
        """Rectifie une durée à l'état haut PWM de la commande des gaz
        Applique uniquement la rectification lorsque la valeur est au dessus de la moitié de ses limites et que l'asssistance est activée

        :param valeur: Valeur PWM
        :type valeur: float
        :return: Valeur PWM rectifiée
        :rtype: float
        """
        valeur = valeur * 10 ** (6)
        moitie_gaz = (self.__config_gaz["etat_actif_min"] + self.__config_gaz["etat_actif_max"]) / 2
        if self.__assistance_flat and valeur >= moitie_gaz:
            valeur = self.__rectifier_flat(valeur, self.__config_gaz)
        return valeur * 10 ** (-6)

    def rectifier_profondeur(self, valeur: float, pitch: float | None) -> float:
        """Rectifie une durée à l'état haut PWM de la commande de la profondeur
        Applique uniquement la rectification lorsque l'asssistance flat est activée
        et/ou 
        que l'asssistance dynamique est activé

        :param valeur: Valeur PWM
        :type valeur: float
        :param pitch: pitch actuelle
        :type pitch: float
        :return: Valeur PWM rectifiée
        :rtype: float
        """
        valeur = valeur * 10 ** (6)
        # Si la commande est au milieu et que l'assistance dynamique est activé on applique le PID
        # Il faut que le PID soit reset avant chaque application du régulateur PID
        # on ne peut pas reprendre avec un PID qui a potentiellement dévié (car pdt un laps de temps l'avion n'a pas répondu à ses commandes)
        if self.__assistance_dynamique and (pitch is not None) and ((self.__middle_point_profondeur - self.__assistance_dynamique_PID_range) <= valeur <= (self.__middle_point_profondeur + self.__assistance_dynamique_PID_range)):

            # Permet de reset le PID avant l'activation du PID
            if self.__end_PID_profondeur:
                self.__profondeur_PID.reset()
                self.__end_PID_profondeur = False

            nouvelle_valeur = self.__profondeur_PID(pitch)
            nouvelle_valeur = self.map(nouvelle_valeur, self.__config_profondeur["angle_min"], self.__config_profondeur["angle_max"], self.__config_profondeur["etat_actif_min"], self.__config_profondeur["etat_actif_max"])
            return nouvelle_valeur * 10 **(-6)
        else:
            self.__end_PID_profondeur = True

        if self.__assistance_flat:
            valeur = self.__rectifier_flat(valeur, self.__config_profondeur)
        return valeur * 10 **(-6)

    def rectifier_ailerons(self, valeur: float, roll: float | None) -> float:
        """Rectifie une durée à l'état haut PWM de la commande des ailerons
        Applique uniquement la rectification lorsque l'asssistance flat est activée
        et/ou 
        que l'asssistance dynamique est activé

        :param valeur: Valeur PWM
        :type valeur: float
        :param roll: roll actuelle
        :type roll: float
        :return: Valeur PWM rectifiée
        :rtype: float
        """
        valeur = valeur * 10 ** (6)
        # Si la commande est au milieu et que l'assistance dynamique est activé on applique le PID
        # Il faut que le PID soit reset avant chaque application du régulateur PID
        # on ne peut pas reprendre avec un PID qui a potentiellement dévié (car pdt un laps de temps l'avion n'a pas répondu à ses commandes)
        if self.__assistance_dynamique and (roll is not None) and ((self.__middle_point_ailerons - self.__assistance_dynamique_PID_range) <= valeur <= (self.__middle_point_ailerons + self.__assistance_dynamique_PID_range)):

            # Permet de reset le PID avant l'activation du PID
            if self.__end_PID_ailerons:
                self.__ailerons_PID.reset()
                self.__end_PID_ailerons = False

            nouvelle_valeur = self.__ailerons_PID(roll)
            nouvelle_valeur = self.map(nouvelle_valeur, self.__config_ailerons["angle_min"], self.__config_ailerons["angle_max"], self.__config_ailerons["etat_actif_min"], self.__config_ailerons["etat_actif_max"])
            return nouvelle_valeur * 10 ** (-6)
        else:
            self.__end_PID_ailerons = True

        if self.__assistance_flat:
            valeur = self.__rectifier_flat(valeur, self.__config_ailerons)
        return valeur * 10 ** (-6)

    def rectifier_direction(self, valeur: float) -> float:
        """Rectifie une durée à l'état haut PWM de la commande des ailerons
        Applique uniquement la rectification lorsque l'asssistance flat est activée

        :param valeur: Valeur PWM
        :type valeur: float
        :return: Valeur PWM rectifiée
        :rtype: float
        """
        valeur = valeur * 10 ** (6)
        if self.__assistance_flat:
            valeur = self.__rectifier_flat(valeur, self.__config_direction)
        return valeur * 10 ** (-6)

    @property
    def assistance_flat(self) -> bool | float:
        """Getter Assistance Flat

        Le return dépend de la valeur de la variable "rectification_fixe_etat_actif_mid_air" dans le fichier de configuration
        :return: Si l'activation est activé | la force de l'assistance en durée à l'état haut
        :rtype: bool | float
        """
        return self.__assistance_flat

    @assistance_flat.setter
    def assistance_flat(self, valeur: float) -> None:
        """Setter Assistance Flat

        Le type final d'assistance flat dépend de la valeur de la variable "rectification_fixe_etat_actif_mid_air" dans le fichier de configuration
        :param valeur: valeur du canal 5 en durée à l'état haut
        :type valeur: float
        """
        # Assistance flat est la force de l'assistance en durée à l'état haut
        if self.__assistance_flat_dynamique:
            self.__assistance_flat = valeur
        
        # Assistance flat switch de désactivé à activé
        else:
            if valeur > 1500 * 10 ** (-6):
                self.__assistance_flat = False
            else:
                self.__assistance_flat = True

    @property
    def assistance_dynamique(self) -> bool:
        """ Getter Assistance Dynamique

        :return: Si l'assistance Dynamique (PID) est activé
        :rtype: bool
        """
        return self.__assistance_dynamique

    @assistance_dynamique.setter
    def assistance_dynamique(self, valeur: float) -> None:
        """ Setter Assistance Dynamique

        :param valeur: valeur du canal 6 en durée à l'état haut
        :type valeur: float
        """
        if valeur > 1500 * 10 ** (-6):
            self.__assistance_dynamique = False
        else:
            self.__assistance_dynamique = True

    def boolean(self) -> bool:
        """Si l'assistance est activé

        :return: Si l'assistance est activé
        :rtype: bool
        """
        return bool(self.__assistance_flat or self.__assistance_dynamique)
