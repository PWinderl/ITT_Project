from PyQt5 import QtWidgets, QtCore, QtGui
import sys


# To call when Game is over
from PyQt5.QtCore import QSize


class Highscore(QtWidgets.QWidget):
    icon_size: QSize
    imagePath = "out.jpg"

    def __init__(self, score):
        super(Highscore, self).__init__()
        self.score_pair = []
        self.icon_size = QtCore.QSize(100, 80)
        self.new_score = score
        self.img = QtGui.QPixmap(self.imagePath)
        self.score_pair.append([555, self.img])
        self.highscore_table = QtWidgets.QTableWidget(parent=self)
        self.highscores = [1, 2, 3, 4, 11, 6, 7, 8, 9, 10]
        self.init_ui()

    def init_ui(self):
        self.setGeometry(0, 0, 1000, 600)
        self.setWindowTitle('Highscores')
        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.highscore_table, 1, 1)
        self.setLayout(layout)
        self.show()

    def highscore_chart(self):
        print('Highscore_chart: ', self.new_score)
        new_list = sorted(self.highscores, reverse=True)
        print('Sortiert im Chart: ', new_list)
        if self.new_score > new_list[-1]:
            actual_hs_list = self.set_highscores()
            self.draw_highscores(actual_hs_list)
        else:
            self.draw_highscores(self.highscores)

    # Appends new score to highscore list
    def set_highscores(self):
        new_list = sorted(self.highscores, reverse=True)
        if new_list[-1] < self.new_score:
            del new_list[-1]
            new_list.append(self.new_score)
        else:
            pass
        return new_list

    # Draws Table with highscores
    def draw_highscores(self, actual_list):
        new_list = sorted(actual_list, reverse=True)
        self.highscore_table.setRowCount(10)
        self.highscore_table.setColumnCount(2)
        i = 0
        for item in new_list:
            new_entry = QtWidgets.QTableWidgetItem(str(item))
            self.highscore_table.setItem(i, 1, new_entry)
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

    print('im draw widget')
    # pyqtsignal for the recognition at the end of each drawing interaction
    finished_unistroke = QtCore.pyqtSignal(object, bool, str)

    def __init__(self, score):
        super(DrawWidget, self).__init__()
        self.width = 600
        self.height = 400
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
        self.hs = Highscore(43)
        self.dw = DrawWidget(score)
        self.dw.set_callback(self.hs.highscore_chart)
