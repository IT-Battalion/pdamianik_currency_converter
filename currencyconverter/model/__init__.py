from typing import Callable

from .source import Source
from .local import Local
from .exchangeratesio import ExchangeRatesIO
from .builtin import Builtin

"""
This module contains the model classes for the currency converter. The model
classes are responsible for retrieving the exchange rates from various sources.
"""

SOURCES: dict[str, tuple[Callable[[dict], Source], dict]] = {
    Builtin.__name__: (Builtin, {}),
    Local.__name__: (Local, {'path': ('path', 'Exchange Rate Data Path', 'JSON files (*.json)', '.')}),
    ExchangeRatesIO.__name__: (ExchangeRatesIO, {'apikey': (str, 'API Key', 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', '')}),
}
