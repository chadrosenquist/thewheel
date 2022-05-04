"""Tests config.py"""
import io
import unittest
from unittest.mock import patch

import thewheel.config
import thewheel.version


class ConfigTestCase(unittest.TestCase):
    """Tests config.py"""
    def test_short_options(self):
        test_config = thewheel.config.Config(['-sINTL', '-d.3', '-r.03'])
        self.assertEqual('INTL', test_config.stock)
        self.assertAlmostEqual(.3, test_config.delta)
        self.assertAlmostEqual(.03, test_config.delta_range)

    def test_long_options(self):
        test_config = thewheel.config.Config(['--stock=INTL', '--delta=.3', '--range=.03'])
        self.assertEqual('INTL', test_config.stock)
        self.assertAlmostEqual(.3, test_config.delta)
        self.assertAlmostEqual(.03, test_config.delta_range)

    def test_default_options(self):
        test_config = thewheel.config.Config(['--stock=INTL'])
        self.assertEqual('INTL', test_config.stock)
        self.assertAlmostEqual(thewheel.config.DEFAULT_DELTA, test_config.delta)
        self.assertAlmostEqual(thewheel.config.DEFAULT_RANGE, test_config.delta_range)

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
            thewheel.config.Config(['-d.3'])
        self.assertIn('Print help', mock_stdout.getvalue())


if __name__ == '__main__':
    unittest.main()
