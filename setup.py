#!/usr/bin/env python3
# coding: utf-8

"""
By Thomas Oswald
"""

from PyQt5 import QtWidgets, QtCore
from bt_input import Device
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
        except Exception as e:
            print(e)


class SetupWidget(QtWidgets.QWidget):

    on_setup_end = QtCore.pyqtSignal(object)

    DEVICE_LIMIT = 1

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
        layout = QtWidgets.QHBoxLayout(self)

        self.player = QtWidgets.QLabel("Trying to connect player ...")
        layout.addWidget(self.player, alignment=QtCore.Qt.AlignLeft)

        self.conductor = QtWidgets.QLabel("Trying to connect conductor ...")
        layout.addWidget(self.conductor, alignment=QtCore.Qt.AlignRight)

        self.setLayout(layout)
        self.show()

    def on_device_found(self, device):
        self.devices.append(device)
        length = len(self.devices)
        if length == 1:
            self.player.setText("Connected player.")
            self.player.repaint()
        elif length == 2:
            self.conductor.setText("Connected conductor.")
            self.conductor.repaint()
        if len(self.devices) == self.DEVICE_LIMIT:
            sleep(2)
            self.on_setup_end.emit(self.devices)
