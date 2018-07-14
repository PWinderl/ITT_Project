#!/usr/bin/env python3
# coding: utf-8

from PyQt5 import QtWidgets, QtCore

# TODO: This widget should show a starting screen and request the players to connect their wiimotes


class SetupWidget(QtWidgets.QWidget):

    on_setup_end = QtCore.pyqtSignal()

    def __init__(self, size, parent=None):
        super(SetupWidget, self).__init__(parent)
        self.width, self.height = size
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(self.width, self.height)
        layout = QtWidgets.QHBoxLayout(self)

        label = QtWidgets.QLabel("Connect player 1")
        layout.addWidget(label, alignment=QtCore.Qt.AlignLeft)

        label = QtWidgets.QLabel("Connect player 2")
        layout.addWidget(label, alignment=QtCore.Qt.AlignRight)

        self.setLayout(layout)
        self.show()

    # For testing purposes
    def emit(self):
        # Run through
        self.on_setup_end.emit()
