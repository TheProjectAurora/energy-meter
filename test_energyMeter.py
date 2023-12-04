import unittest
from unittest.mock import patch, mock_open
from energyMeter import energyMeter
import json

class TestEnergyMeter(unittest.TestCase):
    def setUp(self):
        self.energy_meter = energyMeter()

    def test_load_consumption_data_success(self):
        mock_data = '{"processor": {"i7-8650U": 50}, "ram": {"ddr4": 2}, "network": 1}'
        with patch('builtins.open', mock_open(read_data=mock_data)):
            self.energy_meter.load_consumption_data()
            self.assertEqual(self.energy_meter.consumption_data['processor']['i7-8650U'], 50)

if __name__ == '__main__':
    unittest.main()