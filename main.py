from PyQt5 import QtWidgets, QtCore
from menu import MenuWidget
from minigame import MiniGameWidget
import sys


class Display(QtWidgets.QMainWindow):

    def __init__(self):
        super(Display, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Main")
        self.showFullScreen()
        self.window = QtWidgets.QWidget(self)
        self.setCentralWidget(self.window)
        layout = QtWidgets.QVBoxLayout(self.window)

        self.menu = MenuWidget((250, 250), parent=self.window)
        self.mg = MiniGameWidget((500, 500), parent=self.window)

        layout.addWidget(self.menu, alignment=QtCore.Qt.AlignCenter)

        self.window.setLayout(layout)

        self.show()

    def change_widget(self, widget):
        pass

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            QtWidgets.QApplication.quit()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    d = Display()
    sys.exit(app.exec_())
