"""Calls the API (or screen scrapes) to get the options chain."""
from datetime import date

import requests
from bs4 import BeautifulSoup

import thewheel.putcontract

BASE_URL = 'https://www.op' \
           'tionis' \
           'tic' \
           's.com/quotes/stock-option-chains'
HEADERS = {
    'User-Agent': 'Mozilla/5.0'
}


class OptionsAPIException(Exception):
    """Options API Exception"""


def get_html(symbol):
    """Gets the HTML document for a stock symbol.

    :param str symbol: Stock symbol
    :rtype: str
    :returns: HTML document

    ?? TODO - Errors and error checking! ??
    """
    url = f'{BASE_URL}/{symbol}'
    data = {
        'symbol': symbol,
        'chtype': '2',  # 0=Calls and Puts, 1=Calls, 2=Puts
        'nonstd': '-1',  # ?
        'greeks': '1',  # Set to 1 to return greeks (delta)
        # 'mn1min': '1',    # Minimum strike range.
        # 'mn1max': '47',   # Maximum strike range.
        'mn1min': '8',  # Minimum strike range.
        'mn1max': '38',  # Maximum strike range.
        'expmin': '0',  # ?
        'expmax': '2',  # ?
        'ovmin': '0',  # ?
        'ovmax': '6',  # ?
        'strike': '',  # ?
        'expiry': '',  # ?
        'op': 'chains',  # ?
        # 'date': '20220506',  # ?
        'prevsym': symbol,  # ?
        'clear': '0',  # ?
        'v': '1',  # ?
        'prevns': ['-1', symbol],  # ?
    }

    r = requests.post(url, data=data)
    if r.ok:
        return r.text
    else:
        return None


def get_put_contracts(symbol):
    """Returns all the put contracts for a stock.

    :param str symbol: Stock symbol
    :rtype: list[thewheel.putcontract.PutContract]
    :raises OptionsAPIException: Error
    """
    html_contents = get_html(symbol)
    soup = BeautifulSoup(html_contents, 'html.parser')
    for link in soup.find_all('a'):
        onclick = link.attrs.get('onclick', '')
        # Ex: onclick="document.getElementById('expiry').value='2022-05-13'
        if 'expiry' in str(onclick):
            option_date = date.fromisoformat(link.text)

            # Find table it belongs to.
            # <table><tr><td><a href></td></tr></table>
            parent_table = link.parent.parent.parent
            row_count = 0
            for tr in parent_table.find_all('tr'):
                # row 0: colspan
                # row 1: expiry
                # row 2: headers
                # rows 3+: options
                if row_count == 2:
                    # Spot check the columns are in the same order.
                    _check_header_columns(tr)
                if row_count >= 3:
                    # print(tr)
                    pass
                row_count += 1

    return []


def _check_header_columns(tr):
    """Checks the header columns are correct.  If they are different, then the screen
    changes and the screen scaper needs to be updated.

    :param tr: Table row object
    :raises OptionsAPIException: If the columns are incorrect.
    """
    print(tr)