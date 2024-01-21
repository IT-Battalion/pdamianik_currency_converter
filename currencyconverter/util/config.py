import os
import pickle
from os import path

from .appdirs import dirs


def get_config(controller, name: str, config: dict):
    """
    Get the configuration for a source.
    :param controller: The controller to use to request configuration values.
    :param name: The name of the source.
    :param config: The configuration for getting the configuration.
    """
    config_path = path.join(dirs.user_config_dir, name, 'config.bin')

    data = {}
    if path.exists(config_path) and path.isfile(config_path):
        with open(config_path, 'rb') as f:
            data = pickle.load(f)

    for item, params in config.items():
        if item in data:
            if params[0] == 'path' and path.exists(data[item]) and path.isfile(data[item]):
                continue
            if params[0] == str and data[item] is not None:
                continue
        data[item] = configure(controller, params)
    return data


def configure(controller, params):
    """
    Get the configuration for a value from the user.
    :param controller: The controller to use to request configuration values.
    :param params: The parameters for getting the configuration.
    """
    if params[0] == 'path':
        return controller.request_path(params[1], params[2], params[3])
    elif params[0] == str:
        return controller.request_string(params[1], params[2], params[3])


def save_config(name: str, config: dict):
    """
    Save the configuration for a source.
    :param name: The name of the source.
    :param config: The configuration to save.
    """
    config_path = path.join(dirs.user_config_dir, name, 'config.bin')

    if not path.exists(path.dirname(config_path)):
        os.makedirs(path.dirname(config_path))
    with open(config_path, 'wb') as f:
        pickle.dump(config, f)
