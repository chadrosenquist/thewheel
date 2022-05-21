"""Tests config.py"""
import io
import unittest
from unittest.mock import patch

import thewheel.config
import thewheel.version
import thewheel.options_api


class ConfigTestCase(unittest.TestCase):
    """Tests config.py"""
    def test_short_options_call(self):
        test_config = thewheel.config.Config(['-c', '-sINTL', '-d.3', '-r.03'])
        self.assertEqual(thewheel.config.OptionType.CALL,
                         test_config.option_type)
        self.assertEqual('INTL', test_config.stock)
        self.assertAlmostEqual(.3, test_config.delta)
        self.assertAlmostEqual(.03, test_config.delta_range)
        self.assertEqual(thewheel.options_api.DEFAULT_STRIKE_RANGE,
                         test_config.strike_range)
        self.assertEqual('call stock=INTL delta=0.3 range=0.03 strike=14',
                         str(test_config))

    def test_short_options_put(self):
        test_config = thewheel.config.Config(['-p', '-sSPY', '-d.4', '-r.04'])
        self.assertEqual(thewheel.config.OptionType.PUT,
                         test_config.option_type)
        self.assertEqual('SPY', test_config.stock)
        self.assertAlmostEqual(.4, test_config.delta)
        self.assertAlmostEqual(.04, test_config.delta_range)
        self.assertEqual(thewheel.options_api.DEFAULT_STRIKE_RANGE,
                         test_config.strike_range)
        self.assertEqual('put stock=SPY delta=0.4 range=0.04 strike=14',
                         str(test_config))

    def test_long_options_call(self):
        test_config = thewheel.config.Config(['--call',
                                              '--stock=INTL',
                                              '--delta=.3',
                                              '--range=.03',
                                              '--strike=16'])
        self.assertEqual(thewheel.config.OptionType.CALL,
                         test_config.option_type)
        self.assertEqual('INTL', test_config.stock)
        self.assertAlmostEqual(.3, test_config.delta)
        self.assertAlmostEqual(.03, test_config.delta_range)
        self.assertEqual(16, test_config.strike_range)
        self.assertEqual('call stock=INTL delta=0.3 range=0.03 strike=16',
                         str(test_config))

    def test_long_options_put(self):
        test_config = thewheel.config.Config(['--put',
                                              '--stock=VZ',
                                              '--delta=.2',
                                              '--range=.12',
                                              '--strike=16'])
        self.assertEqual(thewheel.config.OptionType.PUT,
                         test_config.option_type)
        self.assertEqual('VZ', test_config.stock)
        self.assertAlmostEqual(.2, test_config.delta)
        self.assertAlmostEqual(.12, test_config.delta_range)
        self.assertEqual(16, test_config.strike_range)
        self.assertEqual('put stock=VZ delta=0.2 range=0.12 strike=16',
                         str(test_config))

    def test_default_options(self):
        test_config = thewheel.config.Config(['--put', '--stock=INTL'])
        self.assertEqual('INTL', test_config.stock)
        self.assertAlmostEqual(thewheel.config.DEFAULT_DELTA, test_config.delta)
        self.assertAlmostEqual(thewheel.config.DEFAULT_RANGE, test_config.delta_range)
        self.assertEqual(thewheel.options_api.DEFAULT_STRIKE_RANGE,
                         test_config.strike_range)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_version(self, mock_stdout):
        with self.assertRaises(SystemExit):
            thewheel.config.Config(['--version'])
        self.assertEqual(f'{thewheel.version.__version__}\n',
                         mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_help(self, mock_stdout):
        with self.assertRaises(SystemExit):
            thewheel.config.Config(['--help'])
        self.assertIn('Print help', mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_missing_stock(self, mock_stdout):
        with self.assertRaises(SystemExit):
            thewheel.config.Config(['-c', '-d.3'])
        self.assertIn('Missing required stock',
                      mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_missing_call_or_put(self, mock_stdout):
        with self.assertRaises(SystemExit):
            thewheel.config.Config(['-sINTC', '-d.3'])
        self.assertIn('Missing required call and put', mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_both_call_and_put(self, mock_stdout):
        with self.assertRaises(SystemExit):
            thewheel.config.Config(['-c', '-p', '-sINTC', '-d.3'])
        self.assertIn('Cannot specifiy both call and put', mock_stdout.getvalue())


if __name__ == '__main__':
    unittest.main()
