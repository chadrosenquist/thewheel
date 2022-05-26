"""Tests Options API"""
import os
import unittest
from unittest.mock import patch
from urllib import parse
from datetime import date

import responses

import thewheel.options_api
from thewheel.putcontract import PutContract
from thewheel.config import OptionType


class OptionsAPITestCase(unittest.TestCase):
    """Contains common methods for testing puts and calls."""
    @staticmethod
    def _get_html_contents(basefilename):
        path = os.path.join(os.path.dirname(__file__), 'html', f'{basefilename}.html')
        with open(path, encoding='utf-8') as html_file:
            html_contents = html_file.read()
        return html_contents

    def _check_contract(self, expected: PutContract, actual: PutContract):
        self.assertEqual(expected.expiration, actual.expiration)
        self.assertEqual(expected.stock, actual.stock)
        self.assertAlmostEqual(expected.strike, actual.strike)
        self.assertAlmostEqual(expected.delta, actual.delta)
        self.assertAlmostEqual(expected.implied_vol, actual.implied_vol)
        self.assertAlmostEqual(expected.bid, actual.bid)


class PutOptionsAPITestCase(OptionsAPITestCase):
    """Tests puts."""
    @classmethod
    def setUpClass(cls) -> None:
        """Read in HTML files."""
        cls.intc_html = cls._get_html_contents('put_INTC')
        cls.nclh_html = cls._get_html_contents('put_NCLH')
        cls.spy_html = cls._get_html_contents('put_SPY')
        cls.invalid_header_html = cls._get_html_contents('put_invalid_header')

    @responses.activate
    def test_get_html(self):
        """Verify the URL and POST parameters are correct."""
        stock = 'INTC'
        url = f'{thewheel.options_api.BASE_URL}/{stock}'
        responses.add(responses.POST, url,
                      body='<html></html>')

        thewheel.options_api.get_html(stock, OptionType.PUT, 12)

        self.assertEqual(1, len(responses.calls))
        request0 = responses.calls[0].request
        self.assertEqual(url, request0.url)
        self.assertEqual('POST', request0.method)
        post_params = dict(parse.parse_qsl(request0.body))
        self.assertEqual(stock, post_params['symbol'])
        self.assertEqual('2', post_params['chtype'])  # Puts only
        self.assertEqual('1', post_params['greeks'])
        self.assertEqual(stock, post_params['prevsym'])
        self.assertEqual(stock, post_params['prevns'])
        self.assertEqual('12', post_params['mn1min'])
        self.assertEqual('36', post_params['mn1max'])

    def test_intc(self):
        stock = 'INTC'

        with patch('thewheel.options_api.get_html',
                   return_value=self.intc_html):
            contracts = thewheel.options_api.get_put_contracts(stock,
                                                               OptionType.PUT)

        # Spot check some of the contracts.
        contract1 = contracts[3]
        expected1 = PutContract(stock, date(2022, 5, 13), 36.50, -0.0161, 0.7549, .01)
        self._check_contract(expected1, contract1)

        contract2 = contracts[40]
        expected2 = PutContract(stock, date(2022, 5, 20), 40.0, -0.1845, 0.503, 0.39)
        self._check_contract(expected2, contract2)

        contract3 = contracts[133]
        expected3 = PutContract(stock, date(2022, 7, 15), 50.0, -0.8459, 0.3187, 7.25)
        self._check_contract(expected3, contract3)

    def test_nclh(self):
        stock = 'NCLH'

        with patch('thewheel.options_api.get_html',
                   return_value=self.nclh_html):
            contracts = thewheel.options_api.get_put_contracts(stock,
                                                               OptionType.PUT)

        # Spot check some of the contracts.
        contract1 = contracts[0]
        expected1 = PutContract(stock, date(2022, 5, 13), 13.0, -0.0748, 1.4302, 0.08)
        self._check_contract(expected1, contract1)

        contract2 = contracts[40]
        expected2 = PutContract(stock, date(2022, 5, 20), 16.5, -0.5488, 0.9512, 1.34)
        self._check_contract(expected2, contract2)

        contract3 = contracts[133]
        expected3 = PutContract(stock, date(2022, 6, 10), 18.5, -0.7001, 0.782, 3.05)
        self._check_contract(expected3, contract3)

    def test_spy(self):
        stock = 'SPY'

        with patch('thewheel.options_api.get_html',
                   return_value=self.spy_html):
            contracts = thewheel.options_api.get_put_contracts(stock,
                                                               OptionType.PUT)

        # Spot check some of the contracts.
        contract1 = contracts[5]
        expected1 = PutContract(stock, date(2022, 5, 11), 388.0, -0.1927, 0.413, 1.3)
        self._check_contract(expected1, contract1)

        contract2 = contracts[50]
        expected2 = PutContract(stock, date(2022, 5, 13), 404.0, -0.6456, 0.3496, 9.09)
        self._check_contract(expected2, contract2)

        contract3 = contracts[300]
        expected3 = PutContract(stock, date(2022, 6, 13), 405.0, -0.5625, 0.2718, 17.03)
        self._check_contract(expected3, contract3)

    def test_invalid_header_row(self):
        """Tests the header row columns aren't as excepted."""
        stock = 'INTC'

        with patch('thewheel.options_api.get_html',
                   return_value=self.invalid_header_html):
            with self.assertRaises(thewheel.options_api.OptionsAPIException):
                thewheel.options_api.get_put_contracts(stock,
                                                       OptionType.PUT)


class CallOptionsAPITestCase(OptionsAPITestCase):
    """Tests puts."""
    @classmethod
    def setUpClass(cls) -> None:
        """Read in HTML files."""
        cls.intc_html = cls._get_html_contents('call_INTC')

    @responses.activate
    def test_get_html(self):
        """Verify the URL and POST parameters are correct."""
        stock = 'INTC'
        url = f'{thewheel.options_api.BASE_URL}/{stock}'
        responses.add(responses.POST, url,
                      body='<html></html>')

        thewheel.options_api.get_html(stock, OptionType.CALL, 12)

        self.assertEqual(1, len(responses.calls))
        request0 = responses.calls[0].request
        self.assertEqual(url, request0.url)
        self.assertEqual('POST', request0.method)
        post_params = dict(parse.parse_qsl(request0.body))
        self.assertEqual(stock, post_params['symbol'])
        self.assertEqual('1', post_params['chtype'])  # Calls only
        self.assertEqual('1', post_params['greeks'])
        self.assertEqual(stock, post_params['prevsym'])
        self.assertEqual(stock, post_params['prevns'])
        self.assertEqual('12', post_params['mn1min'])
        self.assertEqual('36', post_params['mn1max'])

    def test_intc(self):
        stock = 'INTC'

        with patch('thewheel.options_api.get_html',
                   return_value=self.intc_html):
            contracts = thewheel.options_api.get_put_contracts(stock,
                                                               OptionType.CALL)

        # Spot check some of the contracts.
        contract1 = contracts[3]
        expected1 = PutContract(stock, date(2022, 5, 27), 38.0, 0.9977, 0.3611, 3.6)
        self._check_contract(expected1, contract1)

        contract2 = contracts[40]
        expected2 = PutContract(stock, date(2022, 6, 3), 42.0, 0.4563, 0.3442, 0.77)
        self._check_contract(expected2, contract2)

        contract3 = contracts[133]
        expected3 = PutContract(stock, date(2022, 7, 1), 42.0, 0.4942, 0.3444, 1.65)
        self._check_contract(expected3, contract3)


class StrikeRangeTestCase(unittest.TestCase):
    """Tests check_strike_range."""
    def test_min(self):
        min_strike, max_strike = \
            thewheel.options_api.get_strike_range(5)
        self.assertEqual(19, min_strike)
        self.assertEqual(29, max_strike)

    def test_max(self):
        min_strike, max_strike = \
            thewheel.options_api.get_strike_range(23)
        self.assertEqual(1, min_strike)
        self.assertEqual(47, max_strike)

    def test_too_low(self):
        with self.assertRaises(thewheel.options_api.OptionsAPIException):
            thewheel.options_api.get_strike_range(thewheel.options_api.STRIKE_RANGE_MINIMUM - 1)

    def test_too_high(self):
        with self.assertRaises(thewheel.options_api.OptionsAPIException):
            thewheel.options_api.get_strike_range(thewheel.options_api.STRIKE_RANGE_MAXIMUM + 1)


class CHTypeTestCase(unittest.TestCase):
    """Test get_chtype"""
    def test_call(self):
        result = thewheel.options_api.get_chtype(OptionType.CALL)
        self.assertEqual('1', result)

    def test_put(self):
        result = thewheel.options_api.get_chtype(OptionType.PUT)
        self.assertEqual('2', result)


if __name__ == '__main__':
    unittest.main()
