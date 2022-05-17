"""Tests putcontract.py"""
import unittest
from datetime import date

from thewheel.putcontract import PutContract


class PutContractTestCase(unittest.TestCase):
    """Tests PutContract class"""
    def setUp(self):
        self.contract = PutContract('INTL', date(2022, 5, 20), 45, -0.3186, 0.3713, 0.75)

    def test_init(self):
        contract = self.contract
        self.assertEqual('INTL', contract.stock)
        self.assertEqual(date(2022, 5, 20), contract.expiration)
        self.assertAlmostEqual(45.0, contract.strike)
        self.assertAlmostEqual(-0.3186, contract.delta)
        self.assertAlmostEqual(0.3713, contract.implied_vol)
        self.assertAlmostEqual(0.75, contract.bid)

    def test_premium_percent(self):
        self.assertAlmostEqual(1.6666666666666667, self.contract.premium_percent)

    def test_premium(self):
        self.assertAlmostEqual(75.0, self.contract.premium)

    def test_cost(self):
        self.assertAlmostEqual(4500.0, self.contract.cost)

    def test_str(self):
        self.assertEqual(
            'INTL : 2022-05-20 Strike=  45.00 Premium=  75  1.67% Cost= 4500 IV=0.37 Delta=-0.32',
            str(self.contract)
        )

    def test_range_01(self):
        self.assertTrue(self.contract.is_delta_in_range(0.3, .03))

    def test_range_02(self):
        self.assertTrue(self.contract.is_delta_in_range(-0.3, -.03))

    def test_range_03(self):
        self.assertFalse(self.contract.is_delta_in_range(0.4, .03))

    def test_range_04(self):
        self.assertFalse(self.contract.is_delta_in_range(0.4, .00003))


if __name__ == '__main__':
    unittest.main()
