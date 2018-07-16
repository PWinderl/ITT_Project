#!/usr/bin/env python3
# coding: utf-8

"""
By Thomas Oswald
"""

from PyQt5 import QtWidgets, QtCore
from menu import MenuWidget
from minigame import MiniGameWidget
from highscore import HighscoreWidget
from game import GameWidget
from setup import SetupWidget
import sys

# TODO: Define window size (dependent to resolution)
# TODO: MINIMIZE or FULLSCREEN window OR game minimize and maximize ...


class Display(QtWidgets.QMainWindow):

    RESOLUTION = (1920, 975)

    def __init__(self, addresses=None):
        super(Display, self).__init__()
        self.current_widget = None
        self.init_ui()
        self.devices = []
        if addresses is not None:
            self.addresses = addresses
            self.on_widget_change("setup")
        else:
            self.on_widget_change("menu")

    def init_ui(self):
        self.showFullScreen()
        self.window = QtWidgets.QWidget(self)
        self.setCentralWidget(self.window)
        layout = QtWidgets.QVBoxLayout(self.window)
        self.window.setLayout(layout)

        self.show()

    # TODO: Get display resolution
    def on_widget_change(self, widget_type):
        widget = None
        if widget_type == "setup":
            widget = SetupWidget((500, 500), self.addresses, parent=self.window)
            widget.on_setup_end.connect(lambda d: self.connect_devices(d))
        elif widget_type == "menu":
            widget = MenuWidget((500, 500), self.devices, parent=self.window)
            widget.on_menu.connect(self.on_widget_change)
        elif widget_type == "game":
            widget = GameWidget(
                self.RESOLUTION, self.devices, parent=self.window)
            # self.setWindowState(QtCore.Qt.WindowMinimized)
        elif widget_type == "minigame":
            widget = MiniGameWidget(
                (500, 500), self.devices, parent=self.window)
        elif widget_type == "highscore":
            widget = HighscoreWidget(
                (500, 500), self.devices, parent=self.window)
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

    def connect_devices(self, devices):
        self.devices = devices
        self.on_widget_change("menu")

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            # self.setWindowState(QtCore.Qt.WindowFullScreen)
            QtWidgets.QApplication.quit()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    if len(sys.argv) > 1:
        d = Display(sys.argv[1:])
    else:
        d = Display()
    sys.exit(app.exec_())
