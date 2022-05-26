"""Command Line Interface (cli)"""
import thewheel.config
import thewheel.options_api


def main(argv):
    """Main Event Loop

    * Handle command line options.
    """
    the_config = thewheel.config.Config(argv)

    print(f'Running with: {str(the_config)}')

    try:
        contracts = \
            thewheel.options_api.get_put_contracts(the_config.stock,
                                                   the_config.option_type,
                                                   the_config.strike_range)
    except thewheel.options_api.OptionsAPIException as error:
        print(str(error))
        return 1

    for contract in contracts:
        if contract.is_delta_in_range(the_config.delta, the_config.delta_range):
            print(str(contract))

    return 0
