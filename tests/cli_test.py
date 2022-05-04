"""Tests cli.py"""
import io
import unittest
from unittest.mock import patch

import thewheel.cli
import thewheel.version


class CliTestCase(unittest.TestCase):
    """Simple smoke test to verify everything is hooked up."""
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_version(self, mock_stdout):
        with self.assertRaises(SystemExit):
            thewheel.cli.main(['--version'])
        self.assertEqual(f'{thewheel.version.__version__}\n',
                         mock_stdout.getvalue())


if __name__ == '__main__':
    unittest.main()
