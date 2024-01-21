from .model import Source, SOURCES
from .util.config import get_config, save_config, configure
from .view import View


class Controller:
    """
    Controller class. This class is responsible for the communication between the model and the view.
    """
    source: Source = None
    config: dict = {}
    view: View

    def __init__(self):
        """
        Initiate the controller. Create a View object.
        """
        self.view = View(self, SOURCES)
        self.reset()

    def reset(self):
        """
        Reset the controller. This method is called when the application is started.
        """
        self.choose_source(list(SOURCES.keys())[0])

    def available_currencies(self):
        """
        Get the available currencies from the source.
        """
        return self.source.available_currencies()

    def target_currency(self, currency: str, active: bool):
        """
        Set the state of a target currency inside the model. If active is True, the currency will be added to the list of
        target currencies. If active is False, the currency will be removed from the list of target currencies.
        :param currency: The currency to set the state of.
        :param active: The state to set the currency to.
        """
        if active:
            self.source.add_target_currency(currency)
        else:
            self.source.remove_target_currency(currency)

    def source_currency(self, currency: str):
        """
        Set the source currency inside the model.
        :param currency: The currency to set as the source currency.
        """
        self.source.source_currency(currency)

    def convert(self, amount: float):
        """
        Convert the amount of money from the source currency to the target currencies.
        :param amount: The amount of money to convert.
        """
        conversion = self.source.convert(amount)
        self.view.display_conversion(*conversion)

    def request_string(self, title: str, placeholder: str, default: str = ''):
        """
        Request a string from the user.
        :param title: The title of the dialog.
        :param placeholder: The placeholder text of the input field.
        :param default: The default value of the input field.
        :return: The string the user entered.
        """
        return self.view.request_string(title, placeholder, default)

    def request_path(self, title: str, file_type: str, start_path: str = '.'):
        """
        Request a path from the user.
        :param title: The title of the dialog.
        :param file_type: The file type to filter for.
        :param start_path: The path to start the dialog in.
        """
        return self.view.request_path(title, file_type, start_path)

    def choose_source(self, name: str):
        """
        Choose a source to use.
        :param name: The name of the source to use.
        """
        self.view.reset()
        if self.source is not None:
            save_config(self.source.__class__.__name__, self.source.config)
            self.source.close()
        source_class, config_meta = SOURCES[name]
        config = get_config(self, name, config_meta)
        self.source = source_class(config)
        available_currencies = 0, {}
        try:
            available_currencies = self.source.available_currencies()
        except Exception as e:
            self.view.set_status(e.__class__.__name__)
        self.view.set_available_currencies(available_currencies[0], available_currencies[1])

    def reconfigure(self, option: str):
        """
        Reconfigure an option of the source.
        :param option: The option to reconfigure.
        """
        options = list(SOURCES[self.source.__class__.__name__][1][option])
        options[3] = self.source.config[option]
        self.source.config[option] = configure(self, options)

    def __enter__(self):
        """
        Enter the context of the controller. This method is called when the controller is used as a context manager.
        :return: A new instance of the controller.
        """
        return Controller()

    def close(self):
        """
        Close the controller. This method is called when the application is closed.
        :return:
        """
        if self.source is not None:
            save_config(self.source.__class__.__name__, self.source.config)
            self.source.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context of the controller. This method is called when the controller is used as a context manager.
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self.close()
