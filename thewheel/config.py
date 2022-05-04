"""Handles configuration."""
import sys
import getopt

import thewheel.version


DEFAULT_DELTA = .3
DEFAULT_RANGE = .05


def _print_version():
    print(f'{thewheel.version.__version__}')


def _print_help():
    print('python thewheel [options]')
    print('    -h|--help: Print help')
    print('    -v|--version: Version')
    print('    -s|--stock=: Stock symbol. Required. Ex: NCHL')
    print(f'    -d|--delta=: Delta. Optional. Defaults to {DEFAULT_DELTA}')
    print(f'    -r|--range=: Range for delta. Optional. Defaults to {DEFAULT_RANGE}')
    print('    Ex: python thewheel -sINTL -d.3 -r.03')
    print('    Ex: python thewheel --stock=INTL --delta=.3 --range=.03')


class Config:
    """Read configuration in from command line and holds it."""
    def __init__(self, argv):
        self.stock = None
        self.delta = DEFAULT_DELTA
        self.delta_range = DEFAULT_RANGE

        # Handle command line options.
        options, _ = getopt.getopt(argv,
                                   'vhs:d:r:',
                                   ['version', 'help', 'stock=', 'delta=', 'range='])
        for option, opt_value in options:
            if option in ('-v', '--version'):
                _print_version()
                sys.exit(0)
            elif option in ('-h', '--help'):
                _print_help()
                sys.exit(1)
            elif option in ('-s', '--stock'):
                self.stock = opt_value
            elif option in ('-d', '--delta'):
                self.delta = float(opt_value)
            elif option in ('-r', '--range'):
                self.delta_range = float(opt_value)

        if self.stock is None:
            _print_help()
            sys.exit(1)
