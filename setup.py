#!/usr/bin/env python3
# coding: utf-8

"""
The setup module displays a UI for the connecting of devices.
Furthermore, bluetooth addresses will be used to find a device, assign its led
that are representing the players role and returns these devices (Type: Device) for further use.
LED 1 -> player
LED 2 -> conductor

Author: Thomas Oswald
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from bt_input import Device
from bluetooth import BluetoothError
from time import sleep
import sys


class SetupThread(QtCore.QThread):

    """
    The SetupThread handles the search for the bluetooth addresses.
    It will return a device, when one was found.
    If this is not the case the game can't start and will output an error.
    """

    device_found = QtCore.pyqtSignal(object)
    exception_raised = QtCore.pyqtSignal()

    def __init__(self, addresses, parent=None):
        super(SetupThread, self).__init__(parent)
        self.addresses = addresses

    def run(self):
        try:
            if self.addresses is not None:
                for address in self.addresses:
                    self.device_found.emit(Device(address))
        except ValueError as e:
            print(e)
            print(
                "Game is not able to start, because no bluetooth device could be found.")
            self.exception_raised.emit()
            return


class SetupWidget(QtWidgets.QWidget):

    """
    The SetupWidget is the UI representation of the setup state.
    It will display messages to the users and change according to
    the devices, which are added.
    """

    on_setup_end = QtCore.pyqtSignal(object)

    DEVICE_LIMIT = 1

    def __init__(self, size, parent=None):
        super(SetupWidget, self).__init__(parent)
        self.width, self.height = size
        self.devices = []
        self.init_ui()
        self.setHidden(True)

    def start(self, addresses):
        self.show()
        self.setHidden(False)
        self.setup = SetupThread(addresses)
        self.setup.device_found.connect(self.on_device_found)
        self.setup.exception_raised.connect(lambda: sys.exit())
        self.setup.start()

    def hide(self):
        self.setHidden(True)
        self.close()

    def init_ui(self):
        self.setFixedSize(self.width, self.height)
        layout = QtWidgets.QVBoxLayout(self)
        font = QtGui.QFont("Times", 14, QtGui.QFont.Bold)
        self.player = QtWidgets.QLabel(
            "Player, press the sync button of your Wiimote.")
        self.player.setFont(font)
        self.player.setStyleSheet('color: white')
        layout.addWidget(self.player, alignment=QtCore.Qt.AlignCenter)

        self.conductor = QtWidgets.QLabel(
            "Conductor, press the sync button of your Wiimote.")
        self.conductor.setFont(font)
        self.conductor.setStyleSheet('color: white')
        layout.addWidget(self.conductor, alignment=QtCore.Qt.AlignCenter)

        self.setLayout(layout)

    # When a device is found, it will appended to the devices list.
    # Depending whether a device connected beforehand,
    # the device will be declared as player or conductor.
    # At last a callback is fired, when the DEVICE_LIMIT is reached.
    def on_device_found(self, device):
        if device is not None:
            self.devices.append(device)
        length = len(self.devices)

        # First device will be always the player.
        if length == 1:
            device.setLed(0)
            self.player.setText("Connected player.")
            self.player.repaint()

        # Second device will be always the player.
        elif length == 2:
            device.setLed(1)
            self.conductor.setText("Connected conductor.")
            self.conductor.repaint()
        if len(self.devices) == self.DEVICE_LIMIT:
            sleep(2)
            self.on_setup_end.emit(self.devices)

    def closeEvent(self, event):
        return super().closeEvent(event)
