import sys
sys.path.append(r"c:\Partage\AEROFLY\aerofly")

try:
    from configurateur import Configurateur
    config_path = "/flash/configuration.json"
except ImportError:
    from lib.configurateur import Configurateur
    config_path = "configuration.json"

try:
    import ujson
except ImportError:
    import json

    ujson = json

from .base_test import test


class TestConfigurateur:

    def __init__(self) -> None:
        # Load default config
        with open("/flash/configuration copy.json", "r") as f:
            configuration_json = ujson.load(f)

        with open(config_path, "w") as config:
            config.write(ujson.dumps(configuration_json))

        test(self.test_configurateur(), "test_configurateur")
        test(self.test_missing_key_value(), "test_missing_key_value")
        test(self.test_duplicate_pins(), "test_duplicate_pins")
        test(self.test_condition(), "test_condition")
        test(self.test_invalid_value(), "test_invalid_value")

    def test_configurateur(self):
        with open(config_path, "w") as config:
            config.write(ujson.dumps(""))

        Configurateur()

        with open(config_path, "r") as f:
            configuration_json = ujson.load(f)

        try:
            if configuration_json != "":
                return True
        except KeyError:
            return False
        return False

    def test_missing_key_value(self):
        with open(config_path, "r") as f:
            configuration_json = ujson.load(f)

        del configuration_json["moteur"]["moteur_gaz"]

        with open(config_path, "w") as config:
            config.write(ujson.dumps(configuration_json))

        Configurateur()

        with open(config_path, "r") as f:
            configuration_json = ujson.load(f)

        try:
            configuration_json["moteur"]["moteur_gaz"]
            return True
        except KeyError:
            return False

    def test_duplicate_pins(self):
        with open(config_path, "r") as f:
            configuration_json = ujson.load(f)

        configuration_json["moteur"]["moteur_gaz"]["pin"] = 20
        configuration_json["moteur"]["servo_profondeur"]["pin"] = 20

        with open(config_path, "w") as config:
            config.write(ujson.dumps(configuration_json))

        Configurateur()

        with open(config_path, "r") as f:
            configuration_json = ujson.load(f)

        if configuration_json["moteur"]["moteur_gaz"]["pin"] == configuration_json["moteur"]["servo_profondeur"]["pin"]:
            return False
        else:
            return True
        
    def test_condition(self):
        with open(config_path, "r") as f:
            configuration_json = ujson.load(f)

        configuration_json["communication"]["bus_i2c_IMU"]["baudrate"] = 20

        with open(config_path, "w") as config:
            config.write(ujson.dumps(configuration_json))

        Configurateur()

        with open(config_path, "r") as f:
            configuration_json = ujson.load(f)

        min_result = configuration_json["communication"]["bus_i2c_IMU"]["baudrate"] != 20

        configuration_json["communication"]["bus_i2c_IMU"]["baudrate"] = 1000000

        with open(config_path, "w") as config:
            config.write(ujson.dumps(configuration_json))

        Configurateur()

        with open(config_path, "r") as f:
            configuration_json = ujson.load(f)

        return any([min_result, configuration_json["communication"]["bus_i2c_IMU"]["baudrate"] != 1000000])
    
    def test_invalid_value(self):
        with open(config_path, "r") as f:
            configuration_json = ujson.load(f)

        configuration_json["communication"]["bus_i2c_IMU"]["baudrate"] = "b"

        with open(config_path, "w") as config:
            config.write(ujson.dumps(configuration_json))

        Configurateur()

        with open(config_path, "r") as f:
            configuration_json = ujson.load(f)

        return configuration_json["communication"]["bus_i2c_IMU"]["baudrate"] != "b"


if __name__ == "__main__":
    TestConfigurateur()