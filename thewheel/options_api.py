"""Calls the API (or screen scrapes) to get the options chain."""
from datetime import date

import requests
from bs4 import BeautifulSoup

from thewheel.putcontract import PutContract

BASE_URL = 'https://www.op' \
           'tionis' \
           'tic' \
           's.com/quotes/stock-option-chains'
HEADERS = {
    'User-Agent': 'Mozilla/5.0'
}
EXPECTED_HEADERS = ['Strike', 'Symbol', 'Bid', 'Ask', 'Price',
                    'TPrice', 'Volume', 'OI', 'NS', '\xa0',
                    'IVol', 'Delta', 'Theta', 'Gamma', 'Vega',
                    'Rho', 'Strike']
# Column indices must match with headers above.
STRIKE_COLUMN = 0
DELTA_COLUMN = 11
IV_COLUMN = 10
BID_COLUMN = 2


class OptionsAPIException(Exception):
    """Options API Exception"""


class _State:
    """Simple class to keep track of the state, simplifying
    parameter passing.
    """
    def __init__(self):
        """Constructor"""
        self.expiry_found = False
        self.header_found = False


def get_html(stock):
    """Gets the HTML document for a stock symbol.

    :param str stock: Stock symbol
    :rtype: str
    :returns: HTML document

    ?? TODO - Errors and error checking! ??
    """
    url = f'{BASE_URL}/{stock}'
    data = {
        'symbol': stock,
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
        'prevsym': stock,  # ?
        'clear': '0',  # ?
        'v': '1',  # ?
        'prevns': ['-1', stock],  # ?
    }

    r = requests.post(url, data=data)
    if r.ok:
        return r.text
    else:
        return None


def get_put_contracts(stock):
    """Returns all the put contracts for a stock.

    :param str stock: Stock symbol
    :rtype: list[thewheel.putcontract.PutContract]
    :raises OptionsAPIException: Error
    """
    contracts = []
    state = _State()

    html_contents = get_html(stock)
    soup = BeautifulSoup(html_contents, 'html.parser')
    option_date, parent_table = _find_option_chain_table(soup)

    # Everything is in one big table.
    for tr in parent_table.find_all('tr'):
        # row 0: colspan
        # row 1: expiry
        # row 2: headers
        # rows 3+: options
        if not state.expiry_found:
            option_date = _find_expiry(state, option_date, tr)
        elif state.expiry_found and not state.header_found:
            state.header_found = True
            _check_header_columns(tr)
        else:
            _build_contract_from_row(contracts, state, option_date, stock, tr)

    return contracts


def _find_option_chain_table(soup):
    """Find the table that contains the options chain."""
    parent_table = None
    option_date = None
    for link in soup.find_all('a'):
        onclick = link.attrs.get('onclick', '')
        # Ex: onclick="document.getElementById('expiry').value='2022-05-13'
        if 'expiry' in str(onclick):
            option_date = date.fromisoformat(link.text)

            # Find table it belongs to.
            # <table><tr><td><a href></td></tr></table>
            parent_table = link.parent.parent.parent
            break
    return option_date, parent_table


def _check_header_columns(tr):
    """Checks the header columns are correct.  If they are different, then the screen
    changes and the screen scaper needs to be updated.

    :param tr: Table row object
    :raises OptionsAPIException: If the columns are incorrect.
    """
    actual_headers = []
    for td in tr.find_all('td', recursive=False):
        actual_headers.append(td.text)
    if EXPECTED_HEADERS != actual_headers:
        raise OptionsAPIException(f'Expected headers:\n{EXPECTED_HEADERS}\n '
                                  f'but got:\n{actual_headers}\ntr={tr}')


def _find_expiry(state, option_date, tr):
    """Finds the expiry row."""
    td = tr.find_next('td')
    link = td.find_next('a')
    td_str = str(td)
    if link and 'expiry' in td_str and 'getElementById' in td_str:
        onclick = link.attrs.get('onclick', '')
        if 'expiry' in str(onclick):
            option_date = date.fromisoformat(link.text)
            state.expiry_found = True
            state.header_found = False
    return option_date


def _build_contract_from_row(contracts, state, option_date, stock, tr):
    """Takes a row and returns a contract."""
    td = tr.find_next('td')
    # Check if end of this expiry.
    if td.text == '\xa0':
        state.expiry_found = False
        state.header_found = False

    else:
        column_values = []
        for td in tr.find_all('td', recursive=False):
            column_values.append(td.text)
        strike = float(column_values[STRIKE_COLUMN])
        delta = float(column_values[DELTA_COLUMN])
        implied_vol = float(column_values[IV_COLUMN])
        bid = float(column_values[BID_COLUMN])
        contract = PutContract(stock, option_date,
                               strike, delta, implied_vol, bid)
        contracts.append(contract)
