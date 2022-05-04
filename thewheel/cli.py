"""Command Line Interface (cli)"""
import thewheel.config


def main(argv):
    """Main Event Loop

    * Handle command line options.
    """
    the_config = thewheel.config.Config(argv)

    print(f'Running with: stock={the_config.stock} delta={the_config.delta} '
          f'range={the_config.delta_range}')

    return 0
