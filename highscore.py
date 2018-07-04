from PyQt5 import QtWidgets
import sys


# To call when Game is over
class Highscore(QtWidgets.QWidget):
    def __init__(self, score):
        super(Highscore, self).__init__()
        self.highscore_table = QtWidgets.QTableWidget(parent=self)
        self.highscores = [1, 2, 3, 4, 11, 6, 7, 8, 9, 10]
        self.init_ui(score)

    def init_ui(self, score):
        self.setGeometry(0, 0, 1000, 600)
        self.setWindowTitle('Highscores')
        self.set_highscores(score)
        self.draw_highscores()

        self.show()

    # Appends new score to highscore list
    def set_highscores(self, score):
        print(self.highscores)
        self.highscores.sort()
        print(self.highscores)
        if self.highscores[-1] < score:
            del self.highscores[-1]
            print(self.highscores)
            self.highscores.append(score)
            print(self.highscores)
        else:
            pass
        self.highscores.sort()

    # Draws Table with highscores
    def draw_highscores(self):
        self.highscore_table.setRowCount(10)
        self.highscore_table.setColumnCount(1)
        self.highscores.sort(reverse=True)
        print(self.highscores)
        for item in self.highscores:
            new_entry = QtWidgets.QTableWidgetItem(str(item))
            self.highscore_table.setItem(0, item-1, new_entry)
