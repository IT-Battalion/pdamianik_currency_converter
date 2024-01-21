from typing import Callable

from PyQt6.QtGui import QActionGroup
from PyQt6.QtWidgets import *
from PyQt6 import uic

from currencyconverter.model import Source


class View(QMainWindow):
    """
    This class contains all the widgets that are used in the main window and their signal handlers.
    """

    dsb_amount: QDoubleSpinBox
    cb_currency: QComboBox
    lw_output: QListWidget
    pb_convert: QPushButton

    action_quit: QWidgetAction
    action_reset: QWidgetAction

    menu_source: QMenu

    menu_convert: QMenu
    a_loading_placeholder: QWidgetAction
    a_select_all: QWidgetAction

    """
    A dictionary that contains the short and long form of all available currencies.
    """
    currencies: dict[str, str]

    """
    A dictionary that contains all the actions that are used to configure the sources.
    """
    config_actions: dict[str, list[QWidgetAction]] = {}

    def __init__(self, controller, sources: dict[str, tuple[Callable[[any, dict], Source], dict]]):
        """
        Initialize the main window and all its widgets.
        :param controller: The controller object that is used to communicate with the model.
        :param sources: A dictionary that contains all the available sources and their configuration formats.
        """
        super().__init__()
        uic.loadUi("currencyconverter/view/main.ui", self)
        self.controller = controller

        source_group = QActionGroup(self)
        source_group.setExclusive(True)
        first_action = None
        for source, params in sources.items():
            self.config_actions[source] = []

            menu = QMenu(self)
            menu.setTitle(source)

            action = QWidgetAction(self)
            action.setText('select')
            action.setCheckable(True)
            source_group.addAction(action)
            menu.addAction(action)
            menu.addSeparator()

            self.menu_source.addMenu(menu)

            signal_handler = lambda handler, *args, **kwargs: lambda: handler(*args, **kwargs)
            action.triggered.connect(signal_handler(self.choose_source, source))
            first_action = action if first_action is None else first_action

            for item, config in params[1].items():
                config_action = QWidgetAction(self)
                config_action.setText(config[1])
                config_action.setDisabled(True)
                menu.addAction(config_action)
                self.config_actions[source].append(config_action)

                config_action.triggered.connect(signal_handler(controller.reconfigure, item))
        first_action.setChecked(True)

        self.reset()
        self.action_reset.triggered.connect(controller.reset)

        self.cb_currency.activated.connect(lambda x: controller.source_currency(list(self.currencies.keys())[x]))
        self.pb_convert.clicked.connect(self.convert)

    def choose_source(self, source: str):
        """
        This method is called when a source is selected in the menu.
        :param source: The name of the selected source.
        """
        self.controller.choose_source(source)
        for _, actions in self.config_actions.items():
            for action in actions:
                action.setDisabled(True)

        for action in self.config_actions[source]:
            action.setEnabled(True)

    def build_menu_convert(self, target_currencies: dict[str, str] = None):
        """
        This method is called when the target currencies are changed. It updates the menu that is used to select the
        target currencies.
        :param target_currencies: A dictionary that contains all the available target currencies.
        """
        self.menu_convert.clear()

        if target_currencies is None:
            action = QWidgetAction(self)
            action.setText("Loading...")
            action.setDisabled(True)
            self.menu_convert.addAction(action)
        else:
            for short, long in target_currencies.items():
                action = QWidgetAction(self)
                action.setText(f"{short} - {long}")
                action.setCheckable(True)
                signal_handler = lambda target: lambda active: self.controller.target_currency(target, active)
                action.triggered.connect(signal_handler(short))
                self.menu_convert.addAction(action)

    def reset(self) -> None:
        """
        This method is called when the reset button is pressed. It resets all the widgets to their default values.
        """
        self.dsb_amount.setValue(10.0)
        self.cb_currency.setCurrentIndex(0)
        self.lw_output.clear()
        self.build_menu_convert()

    def set_available_currencies(self, index: int, currencies: dict[str, str]):
        """
        This method is called when the available currencies are changed. It updates the combobox that is used to select
        the source currency and the menu that is used to select the target currencies.
        :param index:
        :param currencies:
        :return:
        """
        self.currencies = currencies
        self.cb_currency.clear()
        self.cb_currency.addItems([f"{short} - {long}" for short, long in currencies.items()])
        self.cb_currency.setCurrentIndex(index)
        self.build_menu_convert(currencies)

    def convert(self):
        """
        This method is called when the convert button is pressed. It sends the amount to be converted to the controller.
        """
        self.controller.convert(self.dsb_amount.value())

    def display_conversion(self, date: str, conversion: list[tuple[str, float, float]]) -> None:
        """
        This method is called when the conversion is finished. It updates the list widget that is used to display the
        conversion result.
        :param date: The date of the source data.
        :param conversion: The result of the conversion.
        """
        self.set_status(f"data from {date}")
        self.lw_output.clear()

        if len(conversion) == 0:
            self.lw_output.addItem('No target currencies selected')

        for converted in conversion:
            self.lw_output.addItem(f" are {round(converted[1], 2)} {self.currencies[converted[0]]} ({converted[0]}) (rate: {converted[2]})")

    def request_string(self, title: str, placeholder: str, default: str = ""):
        """
        This method is called when a string is requested from the user. It displays a dialog that asks the user to enter
        the requested string.
        :param title: The title of the dialog.
        :param placeholder: The placeholder text of the input field.
        :param default: The default value of the input field.
        """
        dialog = QInputDialog(self)
        dialog.setInputMode(QInputDialog.InputMode.TextInput)
        dialog.setWindowTitle(title)
        dialog.setTextValue(default)
        line_edit: QLineEdit = dialog.findChild(QLineEdit)
        line_edit.setPlaceholderText(placeholder)
        if dialog.exec():
            return dialog.textValue()
        return None

    def request_path(self, title: str, file_type: str, start_path: str = '.'):
        """
        This method is called when a path is requested from the user. It displays a dialog that asks the user to select
        the requested path.
        :param title: The title of the dialog.
        :param file_type: The file type of the requested path.
        :param start_path: The path where the dialog should start.
        """
        dialog = QFileDialog(self)
        dialog.setWindowTitle(title)
        dialog.setWindowFilePath(start_path)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        dialog.setNameFilter(file_type)
        return dialog.getOpenFileName()[0]

    def set_status(self, message: str):
        """
        This method is called when the status is changed. It updates the status bar.
        :param message: The new status message.
        """
        self.statusbar.showMessage(message)
