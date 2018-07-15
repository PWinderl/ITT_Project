from PyQt5 import QtWidgets, QtCore, QtGui
from operator import itemgetter
import sys


# To call when Game is over
from PyQt5.QtCore import QSize


class HighscoreWidget(QtWidgets.QWidget):
    # icon_size: QSize
    imagePath = "out.jpg"

    def __init__(self, size, devices, parent=None):
        super(HighscoreWidget, self).__init__(parent)
        self.width, self.height = size
        self.score_pair = []
        self.icon_size = QtCore.QSize(100, 80)
        # handle the score in another way.
        self.new_score = 1
        self.img = QtGui.QPixmap(self.imagePath)
        self.score_pair.append([555, self.img])
        self.highscore_table = QtWidgets.QTableWidget(parent=self)
        self.highscores = [1, 2, 3, 4, 11, 6, 7, 8, 9, 10]

        # Testing new List
        self.highscore_list = [[55, "Fabian"], [44, "Paul"], [66, "Thomas"]]

        self.init_ui()

    def init_ui(self):
        self.setFixedSize(self.width, self.height)
        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.highscore_table, 1, 1)
        self.setLayout(layout)
        self.show()

    def highscore_chart(self):

        # Testing new List
        sorted_hs_list = sorted(self.highscore_list,
                                key=itemgetter(0), reverse=True)
        print(sorted_hs_list)
        print('Score Pair: ', self.score_pair[0][0])
        print('Last HS List Item SCore: ', sorted_hs_list[-1][0])
        if self.score_pair[0][0] > sorted_hs_list[-1][0]:
            new_hs_list = self.set_highscores()
            self.draw_highscores(new_hs_list)
        else:
            print('HS in Else')
            self.draw_highscores(self.highscore_list)

        # print('Highscore_chart: ', self.new_score)
        # new_list = sorted(self.highscores, reverse=True)
        # print('Sortiert im Chart: ', new_list)
        # if self.new_score > new_list[-1]:
        #     actual_hs_list = self.set_highscores()
        #     self.draw_highscores(actual_hs_list)
        # else:
        #     self.draw_highscores(self.highscores)

    # Appends new score to highscore list
    def set_highscores(self):
        # Testing new List
        sorted_hs_list = sorted(self.highscore_list,
                                key=itemgetter(0), reverse=True)
        if sorted_hs_list[-1][0] < self.score_pair[0][0]:
            del sorted_hs_list[-1]
            sorted_hs_list.append(self.score_pair[0])
            print('New Score List with appen: ', sorted_hs_list)
        else:
            pass
        return sorted_hs_list

        # new_list = sorted(self.highscores, reverse=True)
        # if new_list[-1] < self.new_score:
        #     del new_list[-1]
        #     new_list.append(self.new_score)
        # else:
        #     pass
        # return new_list

    # Draws Table with highscores
    def draw_highscores(self, actual_list):
        new_list = sorted(actual_list, key=itemgetter(0), reverse=True)
        self.highscore_table.setRowCount(10)
        self.highscore_table.setColumnCount(2)
        i = 0
        for item in new_list:
            actual_score = item[0]
            if type(item[1]) is not str:
                actual_signature = item[1]
                print('Signature: ', actual_signature)
                sign_to_icon = QtGui.QIcon(QtGui.QPixmap(item[1]))
                new_sign_entry = QtWidgets.QTableWidgetItem(sign_to_icon, "")
                self.highscore_table.setItem(i, 0, new_sign_entry)

            new_score_entry = QtWidgets.QTableWidgetItem(str(actual_score))
            self.highscore_table.setItem(i, 1, new_score_entry)
            self.highscore_table.setRowHeight(i, 60)
            i += 1

        test_icon = QtGui.QIcon(QtGui.QPixmap(self.score_pair[0][1]))
        test_item = QtWidgets.QTableWidgetItem(test_icon, "")
        self.highscore_table.setItem(3, 0, test_item)

        icon = QtGui.QIcon(QtGui.QPixmap("out.jpg"))
        item = QtWidgets.QTableWidgetItem(icon, "")
        self.highscore_table.setItem(2, 0, item)
        self.highscore_table.setIconSize(self.icon_size)
        self.highscore_table.resize(600, 600)

        self.highscores = new_list
        print(self.highscores)


class DrawWidget(QtWidgets.QWidget):

    # pyqtsignal for the recognition at the end of each drawing interaction
    finished_unistroke = QtCore.pyqtSignal(object, bool, str)

    def __init__(self, score):
        super(DrawWidget, self).__init__()
        self.width = 1000
        self.height = 1000
        self.actual_score = score
        self.setMouseTracking(True)
        self.recognize_flag = False
        self.click_flag = False
        self.positions = []
        self.path = QtGui.QPainterPath()
        self.bt_save = QtWidgets.QPushButton(parent=self)
        self.init_ui()
        self.flag = False
        self.t_name = ""
        self.save_callback = None

    def init_ui(self):
        self.setWindowTitle("Signature")
        self.setGeometry(0, 0, self.width, self.height)
        self.setAutoFillBackground(True)

        self.bt_save.setText('Save Highscore')
        self.bt_save.clicked.connect(self.save_highscore)
        self.show()

    def set_callback(self, callback):
        self.save_callback = callback

    def save_highscore(self):
        print('In save_highscore_______')
        signature = QtWidgets.QWidget.grab(self)
        signature.save("out.jpg")
        if self.save_callback is not None:
            self.save_callback()
        self.close()

    def set_name(self, flag, name):
        self.setStyleSheet("background-color:white;")
        self.path = QtGui.QPainterPath()
        self.update()
        self.flag = flag
        self.t_name = name

    def set_cursor(self, x, y):
        QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(x, y)))

    def paintEvent(self, event):
        # img = QtGui.QImage(200, 200, QtGui.QImage.Format_ARGB32)

        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPath(self.path)
        qp.end()

    def d_pad_pushed(self):
        print('D_Pad_Pushed____')

    # callback function for the button press and release event
    # Toggle funcitonality by
    # https://stackoverflow.com/questions/8381735/how-to-toggle-a-value-in-python
    # Pyqtsignal emitting
    def on_click(self):
        print('In onClick____')
        self.recognize_flag ^= True
        self.click_flag ^= True
        if not self.click_flag:
            self.finished_unistroke.emit(
                self.positions, self.flag, self.t_name)

    # mouse moves with mouse or with set_cursor
    def mouseMoveEvent(self, event):
        if self.recognize_flag:
            if self.click_flag:
                self.click_flag = False
                self.path.moveTo(event.pos())
                self.positions.append((event.pos().x(), event.pos().y()))
                self.update()
                return
            self.positions.append((event.pos().x(), event.pos().y()))
            self.path.lineTo(event.pos())
            self.update()

    def mousePressEvent(self, event):
        self.recognize_flag = True
        self.path.moveTo(event.pos())
        self.update()

    def mouseReleaseEvent(self, event):
        self.recognize_flag = False
        self.finished_unistroke.emit(self.positions, self.flag, self.t_name)
        self.positions = []


class HighscoreHandler():
    def __init__(self, score):
        super(HighscoreHandler, self).__init__()
        self.hs = HighscoreWidget(43)
        self.dw = DrawWidget(score)
        self.dw.set_callback(self.hs.highscore_chart)
