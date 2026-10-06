import ujson


class Configurateur:
    """Classe configurateur.
    Permet l'import d'un json
    Permet la vérification des valeurs importé
    """
    def __init__(self) -> None:
        """Constructeur Configurateur
        """
        self.__used_pins = []
        self.__default_config = {
            "moteur": {
                "moteur_gaz": {
                    "pin": 23,
                    "frequence": 100,
                    "etat_actif_min": 1000,
                    "etat_actif_max": 2000
                },
                "servo_profondeur": {
                    "pin": 22,
                    "frequence": 100,
                    "etat_actif_min": 1000,
                    "etat_actif_max": 2000,
                    "angle_min": -97,
                    "angle_max": 97
                },
                "servo_ailerons1": {
                    "pin": 20,
                    "frequence": 100,
                    "etat_actif_min": 1000,
                    "etat_actif_max": 2000,
                    "angle_min": -97,
                    "angle_max": 97
                },
                "servo_ailerons2": {
                    "pin": 19,
                    "frequence": 100,
                    "etat_actif_min": 1000,
                    "etat_actif_max": 2000,
                    "angle_min": -97,
                    "angle_max": 97
                },
                "servo_direction": {
                    "pin": 21,
                    "frequence": 100,
                    "etat_actif_min": 1000,
                    "etat_actif_max": 2000
                }
            },
            "communication": {
                "bus_i2c_IMU": {
                    "pins": ["P9", "P8"],
                    "baudrate": 20000
                },
                "bus_i2c_fast": {
                    "pins": ["P10", "P11"],
                    "baudrate": 400000
                },
                "ibus": {
                    "baudrate": 115200,
                    "pins": ["P2", "P3"],
                    "timeout_chars": 10
                },
                "lora": {
                    "app_eui": "2503250325032503",
                    "app_key": "E9F71F1380719693DBB89E2DAAE2FCD2"
                }
            },
            "composant": {
                "BNO055": {
                    "adresse_i2c_decimal": 40
                },
                "DFR_GNSS_GPS":{
                    "adresse_i2c_decimal": 102
                },
                "SEN0343": {
                    "adresse_i2c_decimal": 0
                },
                "INA3221": {
                    "adresse_i2c_decimal": 65
                },
                "SHT3X": {
                    "adresse_i2c_decimal": 68
                }
            },
            "controleur": {
                "rafraichissement_seconde": 0.02,
                "rafraichissement_lora_seconde": 10
            },
            "assistance": {
                "rectification_dynamique_etat_actif_range_from_middle": 10,
                "Kp_ailerons": 2.31,
                "Ki_ailerons": 0,
                "kp_ailerons": 2.5,
                "Kp_profondeur": 2.31,
                "Ki_profondeur": 0,
                "kp_profondeur": 2.5,
                "rectification_fixe_etat_actif_gaz": 0,
                "rectification_fixe_etat_actif_mid_air": True,
                "rectification_fixe_etat_actif_profondeur": 400,
                "rectification_fixe_etat_actif_ailerons": 400,
                "rectification_fixe_etat_actif_direction": 400
            },
            "debug": True
        }
        self.__test_config = {
            "moteur": {
                "moteur_gaz": {
                    "pin": self.__test_pins,
                    "frequence": lambda key, x,: self.__test_condition(key, x, 5, 1000),
                    "etat_actif_min": lambda key, x,: self.__test_condition(key, x, 500, 1500),
                    "etat_actif_max": lambda key, x,: self.__test_condition(key, x, 1501, 2500)
                },
                "servo_profondeur": {
                    "pin": self.__test_pins,
                    "frequence": lambda key, x,: self.__test_condition(key, x, 5, 1000),
                    "etat_actif_min": lambda key, x,: self.__test_condition(key, x, 500, 1500),
                    "etat_actif_max": lambda key, x,: self.__test_condition(key, x, 1501, 2500),
                    "angle_min": lambda key, x,: self.__test_condition(key, x, -100, -25),
                    "angle_max": lambda key, x,: self.__test_condition(key, x, 25, 100)
                },
                "servo_ailerons1": {
                    "pin": self.__test_pins,
                    "frequence": lambda key, x,: self.__test_condition(key, x, 5, 1000),
                    "etat_actif_min": lambda key, x,: self.__test_condition(key, x, 500, 1500),
                    "etat_actif_max": lambda key, x,: self.__test_condition(key, x, 1501, 2500),
                    "angle_min": lambda key, x,: self.__test_condition(key, x, -100, -25),
                    "angle_max": lambda key, x,: self.__test_condition(key, x, 25, 100)
                },
                "servo_ailerons2": {
                    "pin": self.__test_pins,
                    "frequence": lambda key, x,: self.__test_condition(key, x, 5, 1000),
                    "etat_actif_min": lambda key, x,: self.__test_condition(key, x, 500, 1500),
                    "etat_actif_max": lambda key, x,: self.__test_condition(key, x, 1501, 2500),
                    "angle_min": lambda key, x,: self.__test_condition(key, x, -100, -25),
                    "angle_max": lambda key, x,: self.__test_condition(key, x, 25, 100)
                },
                "servo_direction": {
                    "pin": self.__test_pins,
                    "frequence": lambda key, x,: self.__test_condition(key, x, 5, 1000),
                    "etat_actif_min": lambda key, x,: self.__test_condition(key, x, 500, 1500),
                    "etat_actif_max": lambda key, x,: self.__test_condition(key, x, 1501, 2500)
                }
            },
            "communication": {
                "bus_i2c_IMU": {
                    "pins": self.__test_pins,
                    "baudrate": lambda key, x,: self.__test_condition(key, x, 9600, 30000)
                },
                "bus_i2c_fast": {
                    "pins": self.__test_pins,
                    "baudrate": lambda key, x,: self.__test_condition(key, x, 9600, 400000)
                },
                "ibus": {
                    "baudrate": lambda key, x,: self.__test_condition(key, x, 9600, 400000),
                    "pins": self.__test_pins,
                    "timeout_chars": lambda key, x,: self.__test_condition(key, x, 1, 100)
                },
                "lora": {
                    "app_eui": lambda key, x: len(x) == 16,
                    "app_key": lambda key, x: len(x) == 32,
                }
            },
            "composant": {
                "BNO055": {
                    "adresse_i2c_decimal": lambda key, x,: self.__test_in(key, x, [0x28, 0x29])
                },
                "DFR_GNSS_GPS": {
                    "adresse_i2c_decimal": lambda key, x,: self.__test_in(key, x, [0x66])
                },
                "SEN0343": {
                    "adresse_i2c_decimal": lambda key, x,: self.__test_in(key, x, [0x00])
                },
                "INA3221": {
                    "adresse_i2c_decimal": lambda key, x,: self.__test_in(key, x, [64, 65])
                },
                "SHT3X": {
                    "adresse_i2c_decimal": lambda key, x,: self.__test_in(key, x, [68])
                }
            },
            "controleur": {
                "rafraichissement_seconde": lambda key, x,: self.__test_condition(key, x, 0.0005, 0.1),
                "rafraichissement_lora_seconde": lambda key, x,: self.__test_condition(key, x, 0.25, 60)
            },
            "assistance": {
                "rectification_dynamique_etat_actif_range_from_middle": lambda key, x,: self.__test_condition(key, x, 0, 100),
                "Kp_ailerons": lambda key, x,: self.__test_condition(key, x, 0, 5),
                "Ki_ailerons": lambda key, x,: self.__test_condition(key, x, 0, 5),
                "kp_ailerons": lambda key, x,: self.__test_condition(key, x, 0, 5),
                "Kp_profondeur": lambda key, x,: self.__test_condition(key, x, 0, 5),
                "Ki_profondeur": lambda key, x,: self.__test_condition(key, x, 0, 5),
                "kp_profondeur": lambda key, x,: self.__test_condition(key, x, 0, 5),
                "rectification_fixe_etat_actif_gaz": lambda key, x,: self.__test_condition(key, x, 0, 600),
                "rectification_fixe_etat_actif_mid_air": lambda key, x,: isinstance(x, bool),
                "rectification_fixe_etat_actif_profondeur": lambda key, x,: self.__test_condition(key, x, 0, 600),
                "rectification_fixe_etat_actif_ailerons": lambda key, x,: self.__test_condition(key, x, 0, 600),
                "rectification_fixe_etat_actif_direction": lambda key, x,: self.__test_condition(key, x, 0, 600)
            },
            "debug": lambda key, x: isinstance(x, bool)
        }

        # configuration_json va être modifié sur place
        with open("/flash/configuration.json", "r") as f:
            configuration_json = ujson.load(f)

        try:
            self._debug = configuration_json["debug"]
        except KeyError:
            self._debug = False

        self.__config_test(configuration_json, self.__test_config)
        
        with open("/flash/configuration.json", "w") as config:
            config.write(ujson.dumps(configuration_json))

    def __test_pins(self, key: str, pin) -> bool:
        """Méthode permettant de vérifier:
        - Si un pin est déja utilisé
        - Si un pin est dans la liste des pin utilisable sur un Lopy4

        :param key: Clé dictionnaire, utilise pour le debug
        :type key: str
        :param pin: pin
        :type pin: int | list[str]
        :return: Validité du pin
        :rtype: bool
        """
        if isinstance(pin, list):
            self.__log("liste de pin trouvé: %s" %pin)
            pin1 = int(pin[0][1:])
            pin2 = int(pin[1][1:])
            return any([self.__test_pins(key, pin1), self.__test_pins(key, pin2)])

        if pin in self.__used_pins:
            self.__log("pin %s déjà utilise. Ligne: %s" %(pin, key))
            return False

        if (0 <= pin <= 12) or (19 <= pin <= 23):
            self.__used_pins.append(pin)
            return True
        else:
            self.__log("pin %s non supporté. Ligne: %s" %(pin, key))
            return False

    def __test_condition(self, key, value, cond_min, cond_max) -> bool:
        """Effectue un test conditionnel
        Inclut log et retient les erreurs

        :param key: Clé dictionnaire, utilise pour le debug
        :type key: str
        :param value: Valeur à vérifié
        :type value: int
        :param cond_min: Condition minimal
        :type cond_min: int
        :param cond_max: Condition maximal
        :type cond_max: int
        :return: Validité de la valeur en fonction des conditions données
        :rtype: bool
        """
        try:
            if cond_min <= value <= cond_max:
                return True
            else:
                self.__log("%s ne satisfait pas les conditions: %s <= %s <= %s" %(key, cond_min, value, cond_max))
                return False
        except TypeError:
            self.__log("Erreur %s: %s" %(key, value))
            return False

    def __test_in(self, key, value, liste) -> bool:
        """Test si une valeur est dans une liste
        Inclut log et retient les erreurs

        :param key: Clé dictionnaire, utilise pour le debug
        :type key: str
        :param value: Valeur à vérifié
        :type value: int
        :param liste: liste
        :type liste: int
        :return: Validité de la valeur en fonction des conditions données
        :rtype: bool
        """
        try:
            if value in liste:
                return True
            else:
                self.__log("%s, la valeur %s n'est pas dans la liste: %s" %(key, value, liste))
                return False
        except TypeError:
            self.__log("Erreur %s: %s" %(key, value))
            return False

    def __log(self, message: str) -> None:
        if self._debug:
            print(" ", message, "dans %s" %self.__current_path)

    def __extract_value_from_default_dict(self):
        """ Utilise la configuration par défaut et le chemin actuelle pour trouver une valeur
        la valeur trouvé sera utilisé comme remplacement pour la config testée
        
        from https://stackoverflow.com/questions/43882048/access-a-dictionary-value-with-dynamic-path-using-in-python

        :return: Valeur par défaut à la position voulu
        :rtype: Any
        """
        value = self.__default_config
        for key_or_index in self.__current_path.split("/"):
            value = value[key_or_index]
        return value

    def __config_test(self, config: dict, test_config: dict, path = "") -> None:
        """Test récursivement toutes les valeurs dans un dictionnaire
        Cette méthode va comparer un dictionnaire importé à des conditions dans un dictionnaire
        Si une valeur dans le dictionnaire importé est érroné elle sera remplacer par une valeur par défaut.

        :param config: Dictionnaire à tester
        :type config: dict
        :param test_config: Dictionnaire contenant les tests
        :type test_config: dict
        """
        for (key_default, value_default), (key_test, value_test) in zip(sorted(config.items()), sorted(test_config.items())):
            if path:
                self.__current_path = path + "/" + key_default
            else:
                self.__current_path = key_default
            try:
                if isinstance(value_default, dict):
                    self.__config_test(value_default, value_test, self.__current_path)
                else:
                    if value_test(key_default, value_default) is False:
                        config[key_default] = self.__extract_value_from_default_dict()
            except TypeError as e:
                print("TypeError happened in %s with %s of type %s. Should be a dict type" %(self.__current_path, value_test, type(value_test)))
