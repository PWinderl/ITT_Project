#!/usr/bin/env python3
# coding: utf-8

"""
By Thomas Oswald
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from bt_input import Device
from bluetooth import BluetoothError
from time import sleep


class SetupThread(QtCore.QThread):

    device_found = QtCore.pyqtSignal(object)

    def __init__(self, addresses, parent=None):
        super(SetupThread, self).__init__(parent)
        self.addresses = addresses

    def run(self):
        try:
            if self.addresses is not None:
                for address in self.addresses:
                    self.device_found.emit(Device(address))
        except BluetoothError as e:
            print(e)


class SetupWidget(QtWidgets.QWidget):

    on_setup_end = QtCore.pyqtSignal(object)

    DEVICE_LIMIT = 2

    def __init__(self, size, addresses, parent=None):
        super(SetupWidget, self).__init__(parent)
        self.width, self.height = size
        self.init_ui()
        self.devices = []
        self.setup = SetupThread(addresses)
        self.setup.device_found.connect(self.on_device_found)
        self.setup.start()

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
        self.show()

    # When a device is found, it will appended to the devices list.
    # Depending whether a device connected beforehand,
    # the device will be declared as player or conductor.
    # At last a callback is fired, when the DEVICE_LIMIT is reached.
    def on_device_found(self, device):
        self.devices.append(device)
        length = len(self.devices)

        # First device will be always the player.
        if length == 1:
            self.player.setText("Connected player.")
            self.player.repaint()

        # Second device will be always the player.
        elif length == 2:
            device.leds[1] = False
            device.leds[2] = True
            self.conductor.setText("Connected conductor.")
            self.conductor.repaint()
        if len(self.devices) == self.DEVICE_LIMIT:
            sleep(2)
            self.on_setup_end.emit(self.devices)
