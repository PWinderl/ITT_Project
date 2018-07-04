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
        if score > self.highscores[-1]:
            actual_hs_list = self.set_highscores(score)
            self.draw_highscores(actual_hs_list)
        else:
            self.draw_highscores(self.highscores)

        self.show()

    # Appends new score to highscore list
    def set_highscores(self, score):
        new_list = sorted(self.highscores, reverse=True)
        if new_list[-1] < score:
            del new_list[-1]
            new_list.append(score)
        else:
            pass
        return new_list

    # Draws Table with highscores
    def draw_highscores(self, actual_list):
        new_list = sorted(actual_list, reverse=True)
        self.highscore_table.setRowCount(10)
        self.highscore_table.setColumnCount(1)
        i = 0
        for item in new_list:
            new_entry = QtWidgets.QTableWidgetItem(str(item))
            self.highscore_table.setItem(0, i, new_entry)
            i += 1
        self.highscores = new_list
        print(self.highscores)
