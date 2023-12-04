import unittest
from unittest.mock import patch, mock_open
from energyCalculator import energyCalculator
import json

class TestEnergyCalculator(unittest.TestCase):
    def setUp(self):
        self.energy_calculator = energyCalculator()

    def test_load_consumption_data_success(self):
        mock_data = '{"processor": {"i7-8650U": 50}, "ram": {"ddr4": 2}, "network": 1}'
        with patch('builtins.open', mock_open(read_data=mock_data)):
            self.energy_calculator.load_consumption_data()
            self.assertEqual(self.energy_calculator.consumption_data['processor']['i7-8650U'], 50)

if __name__ == '__main__':
    unittest.main()