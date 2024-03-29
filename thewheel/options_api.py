"""Calls the API (or screen scrapes) to get the options chain."""
from datetime import date

import requests
from bs4 import BeautifulSoup, FeatureNotFound

from thewheel.putcontract import PutContract
import thewheel.config

BASE_URL = 'https://www.op' \
           'tionis' \
           'tic' \
           's.com/quotes/stock-option-chains'
HTTP_HEADERS = {
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

STRIKE_MIDDLE = 24
STRIKE_RANGE_MINIMUM = 5
STRIKE_RANGE_MAXIMUM = 23
DEFAULT_STRIKE_RANGE = 14


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


def get_html(stock, option_type, strike_range):
    """Gets the HTML document for a stock symbol.

    :param str stock: Stock symbol
    :param thewheel.config.OptionType option_type: Put or call.
    :param int strike_range: Strike range
    :rtype: str
    :returns: HTML document

    ?? TODO - Errors and error checking! ??
    """
    min_strike, max_strike = get_strike_range(strike_range)
    chtype = get_chtype(option_type)

    url = f'{BASE_URL}/{stock}'
    data = {
        'symbol': stock,
        'chtype': chtype,  # 0=Calls and Puts, 1=Calls, 2=Puts
        'nonstd': '-1',  # ?
        'greeks': '1',  # Set to 1 to return greeks (delta)
        # 'mn1min': '1',    # Minimum strike range.
        # 'mn1max': '47',   # Maximum strike range.
        # 'mn1min': '8',  # Minimum strike range.
        # 'mn1max': '38',  # Maximum strike range.
        'mn1min': str(min_strike),
        'mn1max': str(max_strike),
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

    r = requests.post(url, data=data, headers=HTTP_HEADERS)
    if r.ok:
        return r.text
    else:
        return None


def get_put_contracts(stock, option_type, strike_range=None):
    """Returns all the put contracts for a stock.

    :param str stock: Stock symbol
    :param thewheel.config.OptionType option_type: Put or call.
    :param int strike_range: Strike range
    :rtype: list[thewheel.putcontract.PutContract]
    :raises OptionsAPIException: Error
    """
    if strike_range is None:
        strike_range = DEFAULT_STRIKE_RANGE
    contracts = []
    state = _State()

    html_contents = get_html(stock, option_type, strike_range)
    try:
        soup = BeautifulSoup(html_contents, 'lxml')
    except FeatureNotFound as error:
        print(f'Warning: lxml not found.  Defaulting to HTML parser. '
              f'Will be slower: {str(error)}')
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


def get_strike_range(strike_range):
    """Returns min and max strike and checks if valid.

    :param int strike_range: Strike range.
    :rtype: int,int
    :returns: minimum and maximum strikes.
    :raises OptionsAPIException: If out of range.
    """
    if strike_range > STRIKE_RANGE_MAXIMUM or \
            strike_range < STRIKE_RANGE_MINIMUM:
        raise OptionsAPIException(f'Strike range of {strike_range} is '
                                  f'not with range of {STRIKE_RANGE_MINIMUM} '
                                  f'to {STRIKE_RANGE_MAXIMUM}')
    min_strike = STRIKE_MIDDLE - strike_range
    max_strike = STRIKE_MIDDLE + strike_range
    return min_strike, max_strike


def get_chtype(option_type):
    """Converts the option_type to a string used in the REST call.

    :param thewheel.config.OptionType option_type: Put or call.
    :rtype: str
    :returns: Option type.
    """
    if option_type is thewheel.config.OptionType.PUT:
        return '2'
    else:
        return '1'
