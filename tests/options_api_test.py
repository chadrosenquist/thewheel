"""Tests Options API"""
import os

import unittest
from unittest.mock import patch
import responses
from urllib import parse

import thewheel.options_api


class OptionsAPITestCase(unittest.TestCase):
    """Tests get_html."""
    @classmethod
    def setUpClass(cls) -> None:
        """Read in HTML files."""
        cls.intc_html = cls._get_html_contents('INTC')

    @staticmethod
    def _get_html_contents(symbol):
        path = os.path.join(os.path.dirname(__file__), 'html', f'{symbol}.html')
        with open(path) as html_file:
            html_contents = html_file.read()
        return html_contents

    @responses.activate
    def test_get_html(self):
        """Verify the URL and POST parameters are correct."""
        symbol = 'INTC'
        url = f'{thewheel.options_api.BASE_URL}/{symbol}'
        responses.add(responses.POST, url,
                      body='<html></html>')

        thewheel.options_api.get_html(symbol)

        self.assertEqual(1, len(responses.calls))
        request0 = responses.calls[0].request
        self.assertEqual(url, request0.url)
        self.assertEqual('POST', request0.method)
        post_params = dict(parse.parse_qsl(request0.body))
        self.assertEqual(symbol, post_params['symbol'])
        self.assertEqual('2', post_params['chtype'])  # Puts only
        self.assertEqual('1', post_params['greeks'])
        self.assertEqual(symbol, post_params['prevsym'])
        self.assertEqual(symbol, post_params['prevns'])
        print(parse.parse_qsl(request0.body))

    def test_put_intc(self):
        symbol = 'INTC'

        with patch('thewheel.options_api.get_html', return_value=self.intc_html):
            contracts = thewheel.options_api.get_put_contracts(symbol)

        for contract in contracts:
            print(contract)

    def test_invalid_header_row(self):
        """Tests the header row columns are as excepted."""
        # TODO
        pass


if __name__ == '__main__':
    unittest.main()
