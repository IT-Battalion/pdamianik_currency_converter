import json

from .source import Source


class Local(Source):
    """
    This source is used to load the data from a local file.
    """
    date: str
    currencies: dict[str, str]
    rates: dict[str, float]

    _target_currencies: list[str] = []
    _source_currency: str = "Loading..."

    def __init__(self, config):
        """
        This method is called when the source is initialized. It gets the configuration from the controller.
        :param config: The configuration for this source.
        """
        super().__init__(config)

        self.config_changed()

    def close(self):
        pass

    def available_currencies(self) -> tuple[int, dict[str, str]]:
        """
        This returns the available currencies and the index of the default currency.
        :return: A tuple containing the index of the default currency and a dictionary that contains all the available
        currencies.
        """
        index = list(self.currencies.keys()).index('EUR')
        index = 0 if index == -1 else index
        self._source_currency = list(self.currencies.keys())[index]
        return index, self.currencies

    def add_target_currency(self, currency: str):
        """
        This method is called when a target currency is added.
        :param currency: The currency that is added.
        """
        self._target_currencies.append(currency)

    def remove_target_currency(self, currency: str):
        """
        This method is called when a target currency is removed.
        :param currency: The currency that is removed.
        """
        self._target_currencies.remove(currency)

    def source_currency(self, currency: str):
        """
        This method is called when the source currency is changed.
        :param currency: The new source currency.
        """
        self._source_currency = currency

    def convert(self, amount: float) -> tuple[str, list[tuple[str, float, float]]]:
        """
        This method is called when the user wants to convert an amount of money.
        :param amount: The amount of money to convert.
        :return: A tuple containing the date of the conversion and a list of tuples containing the target currency, the
        converted amount and the exchange rate.
        """
        return self.date, [(currency, amount / self.rates[self._source_currency] * self.rates[currency], self.rates[currency] / self.rates[self._source_currency]) for currency in self._target_currencies]

    def config_changed(self):
        """
        This method is called when the configuration has changed. It loads the data from the file according to the configuration.
        """
        data = {}
        with open(self.config['path']) as f:
            data = json.load(f)

        self.date = data['date']
        self.currencies = data['currencies']
        self.rates = data['rates']
