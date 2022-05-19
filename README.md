# The Wheel
Program to facilitate options trading.

# Help
```
python thewheel [options]
    -h|--help: Print help
    -v|--version: Version
    -s|--stock=: Stock symbol. Required. Ex: NCHL
    -d|--delta=: Delta. Optional. Defaults to 0.3
    -r|--range=: Range for delta. Optional. Defaults to 0.05
    Ex: python thewheel -sINTL -d.3 -r.03
    Ex: python thewheel --stock=INTL --delta=.3 --range=.03

```

# Code/Design
### Dependencies
* requests - Used to call API.
* responses - Used by unit tests to mock API.
* beautifulsoup4 - Parse HTML.
* lxml - Optional.  Will try to use the BeautifulSoup lxml parser first.
  If not installed, log a warning message and default to the slower
  html parser.

### Performance Testing
To test performance, here is an example:
```
import cProfile

with cProfile.Profile() as pr:
    contracts = thewheel.options_api.get_put_contracts(stock)
pr.print_stats()
```
