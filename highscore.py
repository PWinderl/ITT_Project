from PyQt5 import QtWidgets, QtCore, QtGui
import sys


# To call when Game is over
class Highscore(QtWidgets.QWidget):
    print('In Highscore_________')

    def __init__(self, score):
        super(Highscore, self).__init__()
        self.highscore_table = QtWidgets.QTableWidget(parent=self)
        self.highscores = [1, 2, 3, 4, 11, 6, 7, 8, 9, 10]
        self.init_ui(score)

    def init_ui(self, score):
        self.setGeometry(0, 0, 1000, 600)
        self.setWindowTitle('Highscores')
        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.highscore_table, 1, 1)
        if score > self.highscores[-1]:
            actual_hs_list = self.set_highscores(score)
            self.draw_highscores(actual_hs_list)
        else:
            self.draw_highscores(self.highscores)
        self.setLayout(layout)
        self.show()

    # Appends new score to highscore list
    def set_highscores(self, score):
        print('In set_highscores________')
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
        self.highscore_table.setColumnCount(2)
        i = 0
        for item in new_list:
            new_entry = QtWidgets.QTableWidgetItem(str(item))
            self.highscore_table.setItem(0, i, new_entry)
            i += 1
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
        if self.save_callback is not None:
            self.save_callback()
        # Highscore(self.actual_score)

    def set_name(self, flag, name):
        self.setStyleSheet("background-color:white;")
        self.path = QtGui.QPainterPath()
        self.update()
        self.flag = flag
        self.t_name = name

    def set_cursor(self, x, y):
        QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(x, y)))

    def paintEvent(self, event):
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
        self.hs = Highscore(score)
        self.dw = DrawWidget(score)
        self.dw.set_callback(self.hs.set_highscores(score))
