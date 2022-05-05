"""Models selling a put contract."""

STOCK_PADDING = 5    # Max stock ticker length.
STRIKE_PADDING = 7
STRIKE_PRECISION = 2
PREMIUM_PRECENT_PADDING = 5
PREMIUM_PERCENT_PRECISION = 2
PREMIUM_PADDING = 4
PREMIUM_PRECISION = 0
COST_PADDING = 5
COST_PRECISION = 0
IV_PADDING = 4
IV_PRECISION = 2


class PutContract:
    """Models selling a put contract."""
    def __init__(self, stock, expiration, strike, delta, implied_vol, bid):
        """Constructor

        :param str stock: Name of stock (symbol)
        :param date expiration: Expiration date of the contract
        :param float strike: Strike price
        :param float delta: Delta
        :param float implied_vol: Implied Volatility (IV)
        :param float bid: Current bid
        """
        self.stock = stock
        self.expiration = expiration
        self.strike = strike
        self.delta = delta
        self.implied_vol = implied_vol
        self.bid = bid

    @property
    def premium_percent(self) -> float:
        """Returns the premium as a percentage."""
        return self.bid / self.strike * 100

    @property
    def premium(self) -> float:
        """Returns the premium, in dollars."""
        return self.bid * 100

    @property
    def cost(self) -> float:
        """Returns the cost of the contract."""
        return self.strike * 100

    def __str__(self) -> str:
        """Class as a printable string."""
        return f'{self.stock:{STOCK_PADDING}}: ' \
               f'{self.expiration} ' \
               f'Premium={self.premium:{PREMIUM_PADDING}.{PREMIUM_PRECISION}f}' \
               f' {self.premium_percent:{PREMIUM_PRECENT_PADDING}.{PREMIUM_PERCENT_PRECISION}f}% ' \
               f'Strike={self.strike:{STRIKE_PADDING}.{STRIKE_PRECISION}f} ' \
               f'Cost={self.cost:{COST_PADDING}.{COST_PRECISION}f} ' \
               f'IV={self.implied_vol:{IV_PADDING}.{IV_PRECISION}f}'

    def is_delta_in_range(self, desired_delta: float, delta_range: float) -> bool:
        """Returns true if delta is within the range."""
        abs_delta = abs(self.delta)
        abs_desired_delta = abs(desired_delta)
        abs_delta_range = abs(delta_range)
        low_end = abs_desired_delta - abs_delta_range
        high_end = abs_desired_delta + abs_delta_range
        return low_end <= abs_delta <= high_end
