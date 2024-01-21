import json
import pickle
from os import path
import os
from urllib.parse import urlencode
import requests
from requests.exceptions import Timeout, RequestException

from .source import Source
from ..util.appdirs import dirs


class ApiException(Exception):
    """
    This exception is raised when the https://exchangeratesapi.io API returns an error.
    """
    pass


class ExchangeRatesIO(Source):
    """
    This source uses the https://exchangeratesapi.io API to convert currencies.
    """
    _target_currencies: list[str] = []
    _source_currency: str = "Loading..."
    _cache: dict[str, tuple[str, str, any]] = {}
    _CACHE_PATH = path.join(dirs.user_cache_dir, 'exchangeratesio', 'cache.bin')

    def __init__(self, config: dict):
        super().__init__(config)
        if path.exists(self._CACHE_PATH):
            with open(self._CACHE_PATH, 'rb') as f:
                self._cache = pickle.loads(f.read())
        self._config = config

    def available_currencies(self) -> tuple[int, dict[str, str]]:
        """
        This returns the available currencies and the index of the default currency.
        :return: A tuple containing the index of the default currency and a dictionary that contains all the available
        currencies.
        """
        data = self._request("symbols", {})
        if not data["success"]:
            raise ApiException("API request failed")
        index = list(data['symbols'].keys()).index('EUR')
        index = 0 if index == -1 else index
        self._source_currency = list(data['symbols'].keys())[index]
        return index, data['symbols']

    def add_target_currency(self, currency: str):
        """
        This adds a target currency to the list of target currencies.
        :param currency: The currency to add.
        """
        self._target_currencies.append(currency)

    def remove_target_currency(self, currency: str):
        """
        This removes a target currency from the list of target currencies.
        :param currency: The currency to remove.
        """
        self._target_currencies.remove(currency)

    def source_currency(self, currency: str):
        """
        This sets the source currency.
        :param currency: The new source currency.
        """
        self._source_currency = currency

    def config_changed(self):
        """
        This is called when the configuration has changed.
        """
        pass

    def convert(self, amount: float) -> tuple[str, list[tuple[str, float, float]]]:
        """
        This converts the given amount to all target currencies.
        :param amount: The amount to convert.
        :return: A tuple containing the source currency and a list of tuples containing the target currency, the converted
        amount and the rate.
        """
        try:
            data = self._request("latest", {"base": self._source_currency, "symbols": ",".join(self._target_currencies)})
            if not data or not data["success"]:
                raise ApiException("Invalid API response")
        except (ApiException, RequestException, Timeout, ConnectionError) as e:
            return e.__class__.__name__, []
        return data["date"], [(currency, amount * data["rates"][currency], data["rates"][currency]) for currency in self._target_currencies]

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """
        This is called when the source is closed. It saves the cache.
        """
        if not path.exists(path.dirname(self._CACHE_PATH)):
            os.makedirs(path.dirname(self._CACHE_PATH))
        with open(self._CACHE_PATH, 'wb') as f:
            f.write(pickle.dumps(self._cache))

    def _request(self, endpoint: str, params: dict) -> any:
        """
        This sends a request to the API.
        :param endpoint: The endpoint to send the request to.
        :param params: The parameters to send with the request.
        :return: The parsed response of the API.
        """
        url = f"https://api.apilayer.com/exchangerates_data/{endpoint}?{urlencode(params)}"
        cache_key = f"{endpoint} {urlencode(params)}"
        headers = {'apikey': self.config['apikey']}
        if cache_key in self._cache:
            headers["If-None-Match"] = self._cache[cache_key][0]
            headers["If-Modified-Since"] = self._cache[cache_key][1]
        with requests.request('GET', url, headers=headers) as response:
            if response.status_code == 304:
                return self._cache[cache_key][2]
            elif response.status_code == 200:
                data = json.loads(response.text)
                self._cache[cache_key] = (response.headers.get("ETag"), response.headers.get("Date"), data)
                return data
