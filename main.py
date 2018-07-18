#!/usr/bin/env python3
# coding: utf-8

"""
By Thomas Oswald
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from menu import MenuWidget
from minigame import MiniGameWidget
from highscore import HighscoreWidget
from game import GameWidget
from setup import SetupWidget
import sys


class Constants():

    # modules
    SETUP = 0
    MENU = 1
    GAME = 2
    MINIGAME = 3
    HIGHSCORE = 4


class Display(QtWidgets.QMainWindow):

    WINDOW_SIZE = (500, 500)
    BACKGROUND = "./background.png"
    MINIGAME_TIMER = 5000

    def __init__(self, res, addresses=None):
        super(Display, self).__init__()
        self.current_widget = None
        self.res = res
        self.init_ui()
        self.devices = []

        self.old_score = 0
        self.end_score = 0
        self.game_running = True
        self.game = None
        self.minigame_winner = None
        if addresses is not None:
            self.addresses = addresses
            self.on_widget_change(Constants.SETUP)
        else:
            self.on_widget_change(Constants.MENU)

    def init_ui(self):
        self.showFullScreen()
        self.window = QtWidgets.QWidget(self)
        self.setCentralWidget(self.window)
        layout = QtWidgets.QVBoxLayout(self.window)
        self.window.setLayout(layout)

        self.show()
        self.update()

    def on_widget_change(self, widget_type):
        widget = None
        if widget_type == Constants.SETUP:
            widget = SetupWidget(
                self.WINDOW_SIZE, self.addresses, parent=self.window)
            widget.on_setup_end.connect(lambda d: self.connect_devices(d))
        elif widget_type == Constants.MENU:
            widget = MenuWidget(self.WINDOW_SIZE, self.devices,
                                (Constants.GAME, Constants.HIGHSCORE), parent=self.window)
            widget.on_menu.connect(self.on_widget_change)
        elif widget_type == Constants.GAME:
            widget = GameWidget(
                self.res, self.devices, score=self.old_score, game=self.game, parent=self.window)
            if self.minigame_winner is not None:
                widget.update_score(self.minigame_winner)
                self.minigame_winner = None
            widget.game_end.connect(self.on_game_end)
            self.start_timer(self.on_minigame_start, self.MINIGAME_TIMER)
        elif widget_type == Constants.MINIGAME:
            widget = MiniGameWidget(
                self.WINDOW_SIZE, self.devices, parent=self.window)
            widget.on_end.connect(self.on_minigame_end)
        elif widget_type == Constants.HIGHSCORE:
            widget = HighscoreWidget(
                (500, 650), self.devices, self.end_score, parent=self.window)
        self.change_widget(widget)

    def change_widget(self, widget):
        if widget is None:
            self.window.layout().removeWidget(self.current_widget)
        elif self.current_widget is None:
            self.window.layout().addWidget(widget, alignment=QtCore.Qt.AlignCenter)
        else:
            self.window.layout().replaceWidget(self.current_widget, widget)
            self.current_widget.close()
        self.current_widget = widget
        self.show()

    # Providing score for highscore widget
    def on_game_end(self, score):
        self.game_running = False
        self.end_score = score
        self.on_widget_change(Constants.HIGHSCORE)

    def start_timer(self, callback, ms):
        def handler():
            callback()
            timer.stop()
            timer.deleteLater()
        timer = QtCore.QTimer()
        timer.timeout.connect(handler)
        timer.start(ms)

    def on_minigame_start(self):
        if self.game_running:
            self.old_score = self.current_widget.score
            self.game = self.current_widget.game
            self.current_widget.on_pause()
            self.on_widget_change(Constants.MINIGAME)

    def on_minigame_end(self, name):
        self.minigame_winner = name
        self.on_widget_change(Constants.GAME)
        self.current_widget.on_continue()

    def connect_devices(self, devices):
        self.devices = devices
        self.on_widget_change(Constants.MENU)

    # https://forum.qt.io/topic/40151/solved-scaled-background-image-using-stylesheet/10
    # comment by mbnoimi
    def paintEvent(self, evnt):
        pixmap = QtGui.QPixmap()
        pixmap.load(self.BACKGROUND)
        qp = QtGui.QPainter()
        qp.begin(self)
        pixmap = pixmap.scaled(
            self.res[0], self.res[1], QtCore.Qt.KeepAspectRatioByExpanding)
        qp.drawPixmap(0, 0, pixmap)
        qp.end()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            QtWidgets.QApplication.quit()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    res = app.desktop().screenGeometry()
    res = (res.width(), res.height())
    if len(sys.argv) > 1:
        d = Display(res, sys.argv[1:])
    else:
        d = Display(res)
    sys.exit(app.exec_())
