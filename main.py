from controleur import Controleur
from assistance import Assistance
from busI2C import BusI2C
from composant import MPU6050
from capteur import Gyroscope, Accelerometre
from time import sleep

def main():
    etat_actif_min = 1000 * 10 ** (-6)
    etat_actif_max = 2000 * 10 ** (-6)
    bus_i2c = BusI2C(0)
    mpu = MPU6050(0x68, bus_i2c)
    gyro = Gyroscope(mpu)
    accel = Accelerometre(mpu)
    # assistance = Assistance(gyro, accel, etat_actif_min, etat_actif_max)
    # Controleur(assistance, etat_actif_min, etat_actif_max).mainloop()
    count = 100
    while count > 100:
        print(gyro.get())
        print(accel.get())
        sleep(0.1)
        count -= 1


if __name__ == "__main__":
    main()