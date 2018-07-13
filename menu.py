from PyQt5 import QtWidgets, QtCore


class MenuWidget(QtWidgets.QWidget):

    def __init__(self, size, parent=None):
        super(MenuWidget, self).__init__(parent)
        self.width, self.height = size
        self.init_ui()

    def init_ui(self):
        # self.setGeometry(0, 0, self.width, self.height)
        self.setFixedSize(self.width, self.height)
        w_layout = QtWidgets.QVBoxLayout(self)

        start = QtWidgets.QPushButton(self)
        start.setFixedSize(200, 50)
        start.setText("Start")
        start.clicked.connect(lambda: self.on_click(0))
        w_layout.addWidget(start, alignment=QtCore.Qt.AlignCenter)

        highscore = QtWidgets.QPushButton(self)
        highscore.setFixedSize(200, 50)
        highscore.setText("Highscore")
        highscore.clicked.connect(lambda: self.on_click(1))
        w_layout.addWidget(highscore, alignment=QtCore.Qt.AlignCenter)

        quit_game = QtWidgets.QPushButton(self)
        quit_game.setFixedSize(200, 50)
        quit_game.setText("Quit")
        quit_game.clicked.connect(lambda: self.on_click(2))
        w_layout.addWidget(quit_game, alignment=QtCore.Qt.AlignCenter)
        self.setLayout(w_layout)
        self.show()

    def on_click(self, idx):
        if idx == 0:
            pass
        elif idx == 1:
            pass
        elif idx == 2:
            QtWidgets.QApplication.quit()
