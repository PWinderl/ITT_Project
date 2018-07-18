#!/usr/bin/env python3
# coding: utf-8

"""
By Thomas Oswald
"""


from PyQt5 import QtWidgets, QtCore
from bt_input import Device


class MenuWidget(QtWidgets.QWidget):

    on_menu = QtCore.pyqtSignal(int)

    def __init__(self, size, devices, codes, parent=None):
        super(MenuWidget, self).__init__(parent)
        self.width, self.height = size
        self.GAME, self.HIGHSCORE = codes
        self.init_ui()

    def init_ui(self):
        # self.setGeometry(0, 0, self.width, self.height)
        self.setFixedSize(self.width, self.height)
        w_layout = QtWidgets.QVBoxLayout(self)

        start = QtWidgets.QPushButton(self)
        start.setFixedSize(200, 50)
        start.setText("1: Start")
        start.clicked.connect(lambda: self.on_click(self.GAME))
        w_layout.addWidget(start, alignment=QtCore.Qt.AlignCenter)

        highscore = QtWidgets.QPushButton(self)
        highscore.setFixedSize(200, 50)
        highscore.setText("2: Highscore")
        highscore.clicked.connect(lambda: self.on_click(self.HIGHSCORE))
        w_layout.addWidget(highscore, alignment=QtCore.Qt.AlignCenter)

        quit_game = QtWidgets.QPushButton(self)
        quit_game.setFixedSize(200, 50)
        quit_game.setText("B: Quit (ESC)")
        quit_game.clicked.connect(lambda: self.on_click(-1))
        w_layout.addWidget(quit_game, alignment=QtCore.Qt.AlignCenter)
        self.setLayout(w_layout)
        self.show()

    def connect_devices(self, devices):
        player = devices[0]
        player.register_click_callback(self.on_btn_click)

    def on_btn_click(self, btn, is_down):
        if is_down:
            if btn == Device.BTN_ONE:
                self.on_click(self.GAME)
            elif btn == Device.BTN_TWO:
                self.on_click(self.HIGHSCORE)
            elif btn == Device.BTN_B:
                self.on_click(0)

    def on_click(self, idx):
        if idx == -1:
            QtWidgets.QApplication.quit()
        else:
            self.on_menu.emit(idx)
