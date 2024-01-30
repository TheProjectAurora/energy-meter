import unittest
from unittest.mock import patch, mock_open, MagicMock, Mock
from energyMeter import energyMeter
import json
import psutil


class TestEnergyMeter(unittest.TestCase):
    def setUp(self):
        self.energy_meter = energyMeter()

    def test_load_consumption_data_success(self):
        mock_data = '{"processor": {"i7-8650U": 50}, "ram": {"ddr4": 2}, "network": 1}'
        with patch('builtins.open', mock_open(read_data=mock_data)):
            self.energy_meter.load_consumption_data()
            self.assertEqual(self.energy_meter.consumption_data['processor']['i7-8650U'], 50)

    def test_load_consumption_data_success(self):
        mock_data = '{"processor": {"i7-8650U": 50}, "ram": {"ddr4": 2}, "network": 1}'
        with patch('builtins.open', mock_open(read_data=mock_data)):
            self.energy_meter.load_consumption_data()
            self.assertEqual(self.energy_meter.consumption_data['processor']['i7-8650U'], 50)

    def test_find_process_cmd(self):
        with patch('psutil.process_iter') as mock_process_iter:
            mock_process = MagicMock()
            mock_process.info = {'name': 'test_process', 'cmdline': ['python', 'test.py']}
            mock_process.parent = Mock(side_effect = psutil.NoSuchProcess(0))
            mock_process_iter.return_value = [mock_process]
            result = self.energy_meter.find_process('test_process', 'python')
            for process in result:
                self.assertEqual(process.info, mock_process.info)

    def test_find_process_name(self):
        with patch('psutil.process_iter') as mock_process_iter:
            mock_process = MagicMock()
            mock_process.parent = Mock(side_effect = psutil.NoSuchProcess(0))
            mock_process.info = {'name': 'test_process'}
            mock_process_iter.return_value = [mock_process]
            result = self.energy_meter.find_process('test_process')
            for process in result:
                self.assertEqual(process.info, mock_process.info)


    def test_find_process_not_found(self):
        # Mock the psutil.process_iter function
        with patch('psutil.process_iter') as mock_process_iter:
            # Set the return value of the mock process_iter function to an empty list
            mock_process_iter.return_value = []

            # Call the find_process method
            result = self.energy_meter.find_process('nonexistent_process')

            # Assert that the result is None
            self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
