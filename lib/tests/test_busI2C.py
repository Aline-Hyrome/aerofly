
# try:
#     from busI2C import BusI2C
#     from .base_test import test 
# except ImportError:
#     from test import test

from busI2C import BusI2C
from .base_test import test

class TestBusI2C:

    def __init__(self) -> None:
        test(self.test_singleton(), "test_singleton")
        test(self.test_multiple_bus(), "test_multiple_bus")

    def test_singleton(self):
        bus1 = BusI2C(0)
        bus2 = BusI2C(0)
        return bus1 is bus2
    
    def test_multiple_bus(self):
        bus1 = BusI2C(0)
        bus2 = BusI2C(1)
        return bus1 is not bus2

if __name__ == "__main__":
    TestBusI2C()