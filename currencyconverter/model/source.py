from abc import ABC, abstractmethod


class Source(ABC):

    """
    This class is the base class for all sources. It contains the methods that are required for a source to work.
    """

    config: dict

    def __init__(self, config: dict):
        """
        This method is called when the source is initialized. It gets the configuration from the controller.
        :param config: The configuration for this source.
        """
        self.config = config

    @abstractmethod
    def close(self):
        """
        This method is called when the source is closed. It is used to close any open connections/files.
        """
        pass

    @abstractmethod
    def available_currencies(self) -> tuple[int, dict[str, str]]:
        """
        This returns the available currencies and the index of the default currency.
        :return: A tuple containing the index of the default currency and a dictionary that contains all the available
        currencies.
        """
        pass

    @abstractmethod
    def add_target_currency(self, currency: str):
        """
        This method is called when a target currency is added.
        :param currency: The currency that is added.
        """
        pass

    @abstractmethod
    def remove_target_currency(self, currency: str):
        """
        This method is called when a target currency is removed.
        :param currency: The currency that is removed.
        """
        pass

    @abstractmethod
    def source_currency(self, currency: str):
        """
        This method is called when the source currency is changed.
        :param currency: The new source currency.
        """
        pass

    @abstractmethod
    def convert(self, amount: float) -> tuple[str, list[tuple[str, float, float]]]:
        """
        This method is called when the user wants to convert an amount of money.
        :param amount: The amount of money to convert.
        :return: A tuple containing the date of the conversion and a list of tuples containing the target currency, the
        converted amount and the exchange rate.
        """
        pass

    @abstractmethod
    def config_changed(self):
        """
        This method is called when the configuration has changed.
        """
        pass
