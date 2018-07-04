#!/usr/bin/env python
from PyQt5 import QtWidgets
import pygame, sys, time
from pygame.locals import *
# import wiimote


# https://stackoverflow.com/questions/34668981/pygame-unable-to-open-mp3-file
class MusicPlayer:
    def __init__(self):
        pygame.init()
        self.play_music_demo()

    # Demo plays a sample song
    def play_music_demo(self):
        pygame.mixer.music.load("Sample.mp3")
        pygame.mixer.music.play()
        time.sleep(2)
        pygame.mixer.music.stop()
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pass
                    pygame.quit()


class SetupWidget(QtWidgets.QWidget):
    def __init__(self):
        super(SetupWidget, self).__init__()
        self.bt_start = QtWidgets.QPushButton(parent=self)
        self.init_ui()

    def init_ui(self):
        self.setGeometry(0, 0, 1000, 600)
        self.setWindowTitle('Wiimote Hero')
        layout = QtWidgets.QGridLayout(self)

        self.bt_start.setText("Start Game")
        self.bt_start.clicked.connect(self.start_game)
        layout.addWidget(self.bt_start, 0, 0)

        self.show()

    def start_game(self, event):
        bluetooth_con = SetupBluetooth()


# To connect to Wiimotes
class SetupBluetooth:
    def __init__(self, address_one, address_two):
        try:
            self.wm_one = wiimote.connect(address_one)
            self.wm_two = wiimote.connect(address_two)
        except BluetoothError:
            print("no valid bluetooth address")
            sys.exit()
            return


        mp = MusicPlayer()


def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = SetupWidget()
    if len(sys.argv) == 2:
        connect_wiimotes = SetupBluetooth(sys.argv[1], sys.argv[2])
    else:
        pass

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()