import unittest
from unittest.mock import Mock
from lib.communication.ibus import IBUS


class TestIBUS(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        
        
        self.ibus = IBUS(self.bus, 115200, ["P2", "P3"], 10)

    def test_bytes_to_int(self):
        value = self.ibus.bytes_to_int(bytes([0xe8, 0x03]))
        self.assertTrue(value == 1000)
        value = self.ibus.bytes_to_int(bytes([0xD0, 0x07]))
        self.assertTrue(value == 2000)

    def test_decode2(self):
        self.bus.read.side_effect = [bytes([0x20, 0x40]), bytes([0xDC, 0x05, 0xDC, 0x05, 0xDC, 0x05, 0xDC, 0x05, 0xDC, 0x05, 0xDC, 0x05, 0xDC, 0x05, 0xDC, 0x05, 0xDC, 0x05, 0xDC, 0x05 ,0xDC, 0x05, 0xDC, 0x05, 0xDC, 0x05, 0xDC, 0x05, 0x83, 0xF3])]
        self.ibus.decode2()
        self.assertTrue(self.ibus.ch1 == 0.0015)
        self.assertTrue(self.ibus.ch2 == 0.0015)
        self.assertTrue(self.ibus.ch3 == 0.0015)
        self.assertTrue(self.ibus.ch4 == 0.0015)
        self.assertTrue(self.ibus.ch5 == 0.0015)
        self.assertTrue(self.ibus.ch6 == 0.0015)

    def test_decode2_corrompu(self):

        self.bus.read.side_effect = [bytes([0x20, 0x40]), bytes([0xDB, 0x05, 0xDB, 0x05, 0xDB, 0x05, 0xDB, 0x05, 0xDB, 0x05, 0xDB, 0x05, 0xDB, 0x05, 0xDB, 0x05, 0xDB, 0x05, 0xDB, 0x05 ,0xDB, 0x05, 0xDB, 0x05, 0xDB, 0x05, 0xDB, 0x05, 0x83, 0xF3])]
        self.ibus.decode2()
        self.assertTrue(self.ibus.ch1 == 0.001499)
        self.assertTrue(self.ibus.ch2 == 0.001499)
        self.assertTrue(self.ibus.ch3 == 0.001499)
        self.assertTrue(self.ibus.ch4 == 0.001499)
        self.assertTrue(self.ibus.ch5 == 0.001499)
        self.assertTrue(self.ibus.ch6 == 0.001499)

        self.bus.read.side_effect = [bytes([0x20, 0x39]), bytes([0xDB, 0x04, 0xDB, 0x04, 0xDB, 0x04, 0xDB, 0x04, 0xDB, 0x04, 0xDB, 0x04, 0xDB, 0x04, 0xDB, 0x04, 0xDB, 0x04, 0xDB, 0x04 ,0xDB, 0x04, 0xDB, 0x04, 0xDB, 0x04, 0xDB, 0x04, 0x83, 0xF3])]
        self.ibus.decode2()
        self.assertTrue(self.ibus.ch1 == 0.001499)
        self.assertTrue(self.ibus.ch2 == 0.001499)
        self.assertTrue(self.ibus.ch3 == 0.001499)
        self.assertTrue(self.ibus.ch4 == 0.001499)
        self.assertTrue(self.ibus.ch5 == 0.001499)
        self.assertTrue(self.ibus.ch6 == 0.001499)

if __name__ == "__main__":
    unittest.main()