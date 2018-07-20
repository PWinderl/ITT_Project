#!/usr/bin/env python3
# coding: utf-8

"""
The menu module functions as UI connection between the game, the highscore and an exit.

Author: Thomas Oswald
"""


from PyQt5 import QtWidgets, QtCore, QtGui
from bt_input import Device


class MenuWidget(QtWidgets.QWidget):

    """
    This widget displays the three options (game, highscore and exit)
    and recognizes a mouse click or a button press.
    When above occurs, a signal will be fired and the UI will be changed.
    """

    on_menu_end = QtCore.pyqtSignal(int)

    def __init__(self, size, devices, codes, parent=None):
        super(MenuWidget, self).__init__(parent)
        self.width, self.height = size
        self.GAME, self.HIGHSCORE = codes
        self.init_ui()
        self.connect_devices(devices)

    def init_ui(self):
        self.setFixedSize(self.width, self.height)
        w_layout = QtWidgets.QVBoxLayout(self)

        start = QtWidgets.QPushButton(self)
        style = "image-position:left;border:2px solid white;color:white;font-size:20px;"
        style = style + \
            "border-radius:10px;image:url(sprites/one_inactive.png)"
        start.setStyleSheet(style)
        start.setFixedSize(200, 50)
        start.setText("Start")
        start.clicked.connect(lambda: self.on_click(self.GAME))
        w_layout.addWidget(start, alignment=QtCore.Qt.AlignCenter)

        highscore = QtWidgets.QPushButton(self)
        style = "image-position:left;border:2px solid white;color:white;font-size:20px;"
        style = style + \
            "border-radius:10px;image:url(sprites/two_inactive.png)"
        highscore.setStyleSheet(style)
        highscore.setFixedSize(200, 50)
        highscore.setText(" Highscore")
        highscore.clicked.connect(lambda: self.on_click(self.HIGHSCORE))
        w_layout.addWidget(highscore, alignment=QtCore.Qt.AlignCenter)

        quit_game = QtWidgets.QPushButton(self)
        style = "image-position:left;border:2px solid white;color:white;font-size:20px;"
        style = style + "border-radius:10px;image:url(sprites/b_inactive.png)"
        quit_game.setStyleSheet(style)
        quit_game.setFixedSize(200, 50)
        quit_game.setText(" Quit (ESC)")
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
            self.on_menu_end.emit(idx)
