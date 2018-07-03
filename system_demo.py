#!/usr/bin/env python
from PyQt5 import QtWidgets
import pygame, sys, time
from pygame.locals import *


class MusicPlayer:
    def __init__(self):
        pygame.init()
        self.play_music_demo()

    def play_music_demo(self):

        pygame.mixer.music.load("Sample.mp3")
        pygame.mixer.music.play()
        time.sleep(2)
        pygame.mixer.music.stop()

        while True:  # Main Loop

            for event in pygame.event.get():
                if event.type == QUIT:
                    pass
                    pygame.quit()


class SetupWidget(QtWidgets.QWidget):
    def __init__(self):
        super(SetupWidget, self).__init__()
        self.bt_ct_wm_one = QtWidgets.QPushButton(parent=self)
        self.bt_ct_wm_two = QtWidgets.QPushButton(parent=self)
        self.init_ui()

    def init_ui(self):
        self.setGeometry(0, 0, 1000, 600)
        self.setWindowTitle('Wiimote Hero')
        layout = QtWidgets.QGridLayout(self)
        layout.setVerticalSpacing(50)

        self.bt_ct_wm_one.setText("Connect first Wiimote")
        self.bt_ct_wm_one.clicked.connect(self.connect_wiimote)
        layout.addWidget(self.bt_ct_wm_one, 0, 0)

        self.bt_ct_wm_two.setText("Connect second Wiimote")
        self.bt_ct_wm_two.clicked.connect(self.connect_wiimote)
        layout.addWidget(self.bt_ct_wm_two, 0, 1)

        self.show()

    def connect_wiimote(self, event):
        bluetooth_con = SetupBluetooth()


class SetupBluetooth:
    def __init__(self):
        mp = MusicPlayer()


def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = SetupWidget()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()