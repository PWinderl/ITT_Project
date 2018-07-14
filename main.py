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


class Display(QtWidgets.QMainWindow):

    def __init__(self):
        super(Display, self).__init__()
        self.current_widget = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Main")
        self.showFullScreen()
        self.window = QtWidgets.QWidget(self)
        self.setCentralWidget(self.window)
        layout = QtWidgets.QVBoxLayout(self.window)

        self.on_widget_change("setup")

        self.window.setLayout(layout)

        self.show()

    def on_widget_change(self, widget_type):
        widget = None
        if widget_type == "setup":
            widget = SetupWidget((500, 500), parent=self.window)
            widget.on_setup_end.connect(lambda: self.on_widget_change("menu"))
            widget.emit()
        elif widget_type == "menu":
            widget = MenuWidget((500, 500), parent=self.window)
            widget.on_menu.connect(self.on_widget_change)
        elif widget_type == "game":
            widget = GameWidget(parent=self.window)
        elif widget_type == "minigame":
            widget = MiniGameWidget((500, 500), parent=self.window)
        elif widget_type == "highscore":
            score = 1
            widget = HighscoreWidget(score, parent=self.window)
        if widget is not None:
            self.change_widget(widget)

    # TODO: Replacing does not work as expected
    def change_widget(self, widget):
        if widget is None:
            self.window.layout().removeWidget(self.current_widget)
        elif self.current_widget is None:
            self.window.layout().addWidget(widget, alignment=QtCore.Qt.AlignCenter)
        else:
            print("replacing")
            item = self.window.layout().replaceWidget(self.current_widget, widget)
            print(type(item))
            del item
        print(self.current_widget is None)
        self.current_widget = widget
        self.show()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            QtWidgets.QApplication.quit()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    d = Display()
    sys.exit(app.exec_())
