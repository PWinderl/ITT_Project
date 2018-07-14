#!/usr/bin/env python
from PyQt5 import QtWidgets
import pygame
import sys
import time
from pygame.locals import *
import highscore
import bluetooth_input
import wiimote


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
        self.hs = None
        self.player_one = address_one
        self.player_two = address_two
        self.bt_start = QtWidgets.QPushButton(parent=self)
        self.bt_change_player = QtWidgets.QPushButton(parent=self)
        self.player_selection = QtWidgets.QLabel(parent=self)
        self.inst_player_one = QtWidgets.QLabel(parent=self)
        self.inst_player_two = QtWidgets.QLabel(parent=self)
        self.hs_callback = None
        self.init_ui(address_one)

    def init_ui(self, address_one):
        self.setGeometry(0, 0, 1000, 600)
        self.setWindowTitle('Wiimote Hero')
        layout = QtWidgets.QGridLayout(self)

        self.bt_start.setText('Start Game')
        self.bt_start.clicked.connect(self.start_game)
        layout.addWidget(self.bt_start, 0, 0)

        self.bt_change_player.setText('Change Player')
        self.bt_change_player.clicked.connect(self.change_player)
        layout.addWidget(self.bt_change_player, 0, 1)

        self.player_selection.setText(
            'Player 1 is currently Wiimote: ' + str(address_one))
        layout.addWidget(self.player_selection, 0, 2)

        self.inst_player_one.setText('Player 1' + "\n" +
                                     'As the notes comes down you have to play violin as shown below and' + "\n" +
                                     'push the correct button according to the lines.' + "\n" +
                                     'Each correct played note gets you points.' + "\n" +
                                     'During the game there will appear mini games where you have to paint' + "\n" +
                                     'the gesture displayed as fast as possible to gain extra points' + "\n" +
                                     'To paint a gesture hold down the "B"-Button on the back of your device' + "\n" +
                                     'and point with your Wiimote.')
        layout.addWidget(self.inst_player_one, 1, 0)

        self.inst_player_two.setText('Player 2' + "\n" +
                                     'Your task is to compose the notes Player 1 has to play' + "\n" +
                                     'To do so you have to push different Buttons:' + "\n" +
                                     '- A for the first column' + "\n" +
                                     '- B for the second column' + "\n" +
                                     '- 1 for the third column' + "\n" +
                                     '- 2 for the fourth column' + "\n" +
                                     'When mini games starts and you are able to draw \
                                      faster than your opponent' + "\n" +
                                     'points from his score will be substracted')
        layout.addWidget(self.inst_player_two, 1, 1)

        self.setLayout(layout)
        self.show()

    def register_hs_callback(self, callback):
        self.hs_callback = callback

    def start_game(self, event):
        # TODO: Replace with start of the game
        # 44 = Dummy-Score
        # self.hs = highscore.Highscore(44)
        # self.hs = highscore.HighscoreHandler(44)
        # self.hs.show()
        # self.hs_callback()
        pass

    def change_player(self, event):
        old_player_one = self.player_one
        self.player_one = self.player_two
        self.player_two = old_player_one
        self.player_selection.setText(
            'Player 1 is currently Wiimote: ' + str(self.player_one))


# To connect to Wiimotes
# class SetupBluetooth:
#     def __init__(self, address_one, address_two):
#         try:
#             self.wm_one = wiimote.connect(address_one)
#             self.wm_two = wiimote.connect(address_two)
#         except BluetoothError:
#             print("No valid bluetooth addresses.")
#             sys.exit()
#             return


def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = SetupWidget('SysArgv1', 'SysArgv2')
    wm_one = bluetooth_input.SetupBluetooth(1)
    wm_two = bluetooth_input.SetupBluetooth(2)
    if len(sys.argv) == 2:
        wm_one = bluetooth_input.SetupBluetooth(sys.argv[1])
        # wm_two = bluetooth_input.SetupBluetooth(sys.argv[2])
    else:
        print('Please enter two valid bluetooth addresses.')
        # sys.exit()

    hs = highscore.HighscoreHandler(44)

    wm_one.register_move_callback(hs.dw.set_cursor)
    wm_one.register_click_callback(hs.dw.on_click)
    wm_one.register_confirm_callback(hs.dw.save_highscore)
    wm_two.register_move_callback(hs.dw.set_cursor)
    wm_two.register_click_callback(hs.dw.on_click)
    wm_two.register_confirm_callback(hs.dw.save_highscore)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
