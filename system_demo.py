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
    def __init__(self, address_one, address_two):
        super(SetupWidget, self).__init__()
        self.player_one = address_one
        self.player_two = address_two
        self.bt_start = QtWidgets.QPushButton(parent=self)
        self.bt_change_player = QtWidgets.QPushButton(parent=self)
        self.player_selection = QtWidgets.QLabel(parent=self)
        self.init_ui(address_one, address_two)

    def init_ui(self, address_one, address_two):
        self.setGeometry(0, 0, 1000, 600)
        self.setWindowTitle('Wiimote Hero')
        layout = QtWidgets.QGridLayout(self)

        self.bt_start.setText('Start Game')
        self.bt_start.clicked.connect(self.start_game)
        layout.addWidget(self.bt_start, 0, 0)

        self.bt_change_player.setText('Change Player')
        self.bt_change_player.clicked.connect(self.change_player)
        layout.addWidget(self.bt_change_player, 0, 1)

        self.player_selection.setText('Player 1 is currently Wiimote: ' + str(address_one))
        layout.addWidget(self.player_selection, 0, 2)

        self.setLayout(layout)
        self.show()

    def start_game(self, event):
        pass

    def change_player(self, event):
        old_player_one = self.player_one
        self.player_one = self.player_two
        self.player_two = old_player_one
        self.player_selection.setText('Player 1 is currently Wiimote: ' + str(self.player_one))


# To connect to Wiimotes
class SetupBluetooth:
    def __init__(self, address_one, address_two):
        try:
            self.wm_one = wiimote.connect(address_one)
            self.wm_two = wiimote.connect(address_two)
        except BluetoothError:
            print("No valid bluetooth addresses.")
            sys.exit()
            return


def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = SetupWidget('SysArgv1', 'SysArgv2')
    if len(sys.argv) == 2:
        connect_wiimotes = SetupBluetooth(sys.argv[1], sys.argv[2])
    else:
        print('Please enter two valid bluetooth addresses.')
        # sys.exit()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()