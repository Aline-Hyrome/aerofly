import unittest
from unittest.mock import Mock
from lib.composant.BNO055 import BNO055


class TestBNO055(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.bus.readfrom_mem.side_effect = [bytes([0xA0])] + [b"\x00\x00\x00\x00\x00\x00"] * 300
        
        self.imu = BNO055(adresse=0x28, bus_I2C=self.bus)

    # ---------------------- __init__ ---------------------- #

    def test_init_adresse_correct(self):
        bus = Mock()
        bus.readfrom_mem.side_effect = [bytes([0xA0])] + [b"\xFF\xFF\xFF\xFF\xFF\xFF"] * 300
        BNO055(adresse=0x28, bus_I2C=bus)

    def test_init_adresse_incorrect(self):
        bus = Mock()
        bus.readfrom_mem.side_effect = [bytes([0xA0])] + [b"\xFF\xFF\xFF\xFF\xFF\xFF"] * 300

        self.assertRaises(ValueError, BNO055, adresse=0x27, bus_I2C=bus)

    def test_init_composant_repond(self):
        bus = Mock()
        bus.readfrom_mem.side_effect = [bytes([0xA0])] + [b"\xFF\xFF\xFF\xFF\xFF\xFF"] * 300

        BNO055(adresse=0x28, bus_I2C=bus)

    def test_init_mauvais_composant_repond(self):
        bus = Mock()
        bus.readfrom_mem.side_effect = [bytes([0xA1])] + [b"\xFF\xFF\xFF\xFF\xFF\xFF"] * 300
        self.assertRaises(RuntimeError, BNO055, adresse=0x28, bus_I2C=bus)

    def test_init_composant_repond_pas(self):
        bus = Mock()
        bus.readfrom_mem.return_value = None
        self.assertRaises(RuntimeError, BNO055, adresse=0x28, bus_I2C=bus)

    # ---------------------- set_power_mode ---------------------- #

    def test_set_power_mode_sucess(self):
        resultat = self.imu.set_power_mode(0b00000000)
        self.assertTrue(resultat)

    def test_set_power_mode_fail(self):
        resultat = self.imu.set_power_mode(0b10000000)
        self.assertFalse(resultat)

    # ---------------------- set_mode ---------------------- #

    def test_set_mode_sucess(self):
        resultat = self.imu.set_mode(0b00000000)
        self.assertTrue(resultat)

    def test_set_mode_fail(self):
        resultat = self.imu.set_mode(0b10000000)
        self.assertFalse(resultat)

    # ---------------------- set_page_id ---------------------- #

    def test_set_page_id_sucess(self):
        resultat = self.imu.set_page_id(1)
        self.assertTrue(resultat)

    def test_set_page_id_fail(self):
        resultat = self.imu.set_page_id(0)
        self.assertFalse(resultat)

    # ---------------------- read_register ---------------------- #

    def test_read_register_success(self):
        self.bus.readfrom_mem.side_effect = (b"\xFF",)
        resultat = self.imu.read_register(0xA0, 0x00)
        self.assertEqual(resultat, b"\xFF")

    def test_read_register_repond_pas(self):
        self.bus.readfrom_mem.side_effect = OSError("Erreur I2C")
        self.bus.readfrom.side_effect = OSError("Erreur I2C")
        resultat = self.imu.read_register(0xA0, 0x00)
        self.assertIsNone(resultat)

    # ---------------------- write_register ---------------------- #

    def test_write_register_success(self):
        resultat = self.imu.write_register(0xA0, 0x00)
        self.assertTrue(resultat)

    def test_write_register_repond_pas(self):
        self.bus.writeto_mem.side_effect = OSError("Erreur I2C")
        resultat = self.imu.write_register(0xA0, 0x00)
        self.assertFalse(resultat)

    # ---------------------- euler ---------------------- #

    def test_euler_sucess(self):
        self.bus.readfrom_mem.side_effect = (b"\x10\x00\x10\x00\x10\x00", )
        resultat = self.imu.euler()
        self.assertEqual(resultat, [1, 1, 1])

    def test_euler_failed_par_taille(self):
        self.bus.readfrom_mem.side_effect = (b"\x10\x00\x10\x00\x10\x00", )
        resultat = self.imu.euler()
        self.assertEqual(resultat, [1, 1, 1])
        self.bus.readfrom_mem.side_effect = (b"\x01\x00\x01\x00\x01", )
        resultat = self.imu.euler()
        self.assertEqual(resultat, [1, 1, 1])

    def test_euler_failed_imu_repond_pas(self):
        self.bus.readfrom_mem.side_effect = (b"\x10\x00\x10\x00\x10\x00", )
        resultat = self.imu.euler()
        self.assertEqual(resultat, [1, 1, 1])
        self.bus.readfrom_mem.side_effect = OSError("Erreur I2C")
        self.bus.readfrom.side_effect = OSError("Erreur I2C")
        resultat = self.imu.euler()
        self.assertEqual(resultat, [1, 1, 1])
    def test_euler_bad_imu_mode(self):
        self.bus.readfrom_mem.side_effect = (b"\x10\x00\x10\x00\x10\x00", )
        resultat = self.imu.euler()
        self.assertEqual(resultat, [1, 1, 1])
        self.bus.readfrom_mem.side_effect = (b"\x01\x00\x01\x00\x01", )
        resultat = self.imu.euler()
        self.assertEqual(resultat, [1, 1, 1])

    def test_euler_calibration(self):
        bus = Mock()
        # Uniquement roll et pitch possède un offset
        bus.readfrom_mem.side_effect = [bytes([0xA0])] + [b"\x00\x00\x50\x50\x50\x50"] * 300
        imu = BNO055(adresse=0x28, bus_I2C=bus)
        bus.readfrom_mem.side_effect = (b"\x00\x00\x50\x50\x50\x50", )
        resultat = imu.euler()
        self.assertEqual(resultat, [0, 0, 0])

if __name__ == "__main__":
    unittest.main()
