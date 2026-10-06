# main.py -- put your code here!
import ujson
from controleur import Controleur
from configurateur import Configurateur
import pycom
import machine


def main() -> None:
    while True:
        try:
            Configurateur()
            with open("configuration.json", "r") as json:
                config = ujson.load(json)

            pycom.heartbeat(False)
            pycom.rgbled(0xCCCC00)
            controleur = Controleur(config)
            pycom.heartbeat(True)
            pycom.heartbeat(False)
            pycom.rgbled(0x000000)
            controleur.mainloop()
        except OSError as e:
            print(e)
            print("crashed")
            pycom.rgbled(0xFF0000)
            machine.reset()
        except KeyboardInterrupt:
            break

    pycom.rgbled(0xFF0000)

if __name__ == "__main__":
    main()
