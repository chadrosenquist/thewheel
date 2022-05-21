"""Handles configuration."""
import sys
import getopt
from enum import Enum

import thewheel.version
import thewheel.options_api


DEFAULT_DELTA = .3
DEFAULT_RANGE = .05


def _print_version():
    print(f'{thewheel.version.__version__}')


def _print_help():
    print('python thewheel [options]')
    print('    -h|--help: Print help')
    print('    -v|--version: Version')
    print('    -c|--call or -p|--put: Call or Put.  Required.')
    print('    -s|--stock=: Stock symbol. Required. Ex: NCHL')
    print(f'    -d|--delta=: Delta. Optional. Defaults to {DEFAULT_DELTA}')
    print(f'    -r|--range=: Range for delta. Optional. Defaults to {DEFAULT_RANGE}')
    print(f'    --strike=: Range for strike.  Optional.  Defaults to '
          f'{thewheel.options_api.DEFAULT_STRIKE_RANGE}')
    print('    Ex: python thewheel -p -sINTC -d.3 -r.03')
    print('    Ex: python thewheel --call --stock=INTC --delta=.3 --range=.03')


class OptionType(Enum):
    """Represents the option type."""
    PUT = 'put'
    CALL = 'call'


class Config:
    """Read configuration in from command line and holds it."""
    def __init__(self, argv):
        put = False
        call = False
        self.option_type = None
        self.stock = None
        self.delta = DEFAULT_DELTA
        self.delta_range = DEFAULT_RANGE
        self.strike_range = thewheel.options_api.DEFAULT_STRIKE_RANGE

        # Handle command line options.
        options, _ = getopt.getopt(argv,
                                   'vhcps:d:r:',
                                   ['version', 'help', 'call', 'put',
                                    'stock=', 'delta=', 'range=', 'strike='])
        for option, opt_value in options:
            if option in ('-v', '--version'):
                _print_version()
                sys.exit(0)
            elif option in ('-h', '--help'):
                _print_help()
                sys.exit(1)
            elif option in ('-c', '--call'):
                call = True
            elif option in ('-p', '--put'):
                put = True
            elif option in ('-s', '--stock'):
                self.stock = opt_value
            elif option in ('-d', '--delta'):
                self.delta = float(opt_value)
            elif option in ('-r', '--range'):
                self.delta_range = float(opt_value)
            elif option in '--strike':
                self.strike_range = int(opt_value)

        if self.stock is None:
            print('\nMissing required stock (-s|--stock).\n')
            _print_help()
            sys.exit(1)

        if not put and not call:
            print('\nMissing required call and put (-c|--call or -p|--put).\n')
            _print_help()
            sys.exit(1)

        if put and call:
            print('\nCannot specifiy both call and put (-c|--call and -p|--put).\n')
            _print_help()
            sys.exit(1)

        if put:
            self.option_type = OptionType.PUT
        else:
            self.option_type = OptionType.CALL

    def __str__(self) -> str:
        """Returns string representation."""
        return f'{self.option_type.value} stock={self.stock} delta={self.delta} range={self.delta_range} ' \
               f'strike={self.strike_range}'
