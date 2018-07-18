from PyQt5 import QtWidgets, QtCore, QtGui
from operator import itemgetter


# To call when Game is over
class HighscoreWidget(QtWidgets.QWidget):
    imagePath = "out.jpg"

    def __init__(self, size, devices, end_score, parent=None):
        super(HighscoreWidget, self).__init__(parent)
        self.width, self.height = size
        self.wm_one = None
        self.wm_two = None
        self.score_pair = []
        self.img = None
        self.icon_size = QtCore.QSize(100, 80)
        # TODO: Score from game.py
        self.new_score = end_score
        print('New Score in HW: ', self.new_score)
        self.highscore_table = QtWidgets.QTableWidget(parent=self)
        self.highscore_list = [[55, "Fabian"], [44, "Paul"], [66, "Thomas"], [44, "Paul"], [44, "Paul"], [44, "Paul"],
                               [44, "Paul"], [44, "Paul"], [44, "Paul"], [44, "Paul"]]

        self.init_ui()

        # TODO: Hier abfangen ob vom Menü aus gestartet oder nach Game end
        # TODO: Anschließend Draw Highscores mit highscore list aufrufen
        if self.new_score != 0:
            print('Ist nicht Null')
            self.dw = DrawWidget()
            self.dw.set_callback(self.highscore_chart)
            self.init_devices(devices)
        else:
            print('Ist Null')
            self.draw_highscores(self.highscore_list)
        ###

    def init_ui(self):
        self.setFixedSize(self.width, self.height)
        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.highscore_table, 1, 1)
        self.setLayout(layout)
        self.show()

    def init_devices(self, devices):
        if len(devices) == 1:
            self.wm_one = devices[0]
            self.wm_one.register_move_callback(self.dw.set_cursor)
            self.wm_one.register_click_callback(
                lambda btn, is_down: self.dw.on_click())
            self.wm_one.register_confirm_callback(self.dw.save_highscore)
        elif len(devices) == 2:
            self.wm_one = devices[0]
            self.wm_one.register_move_callback(self.dw.set_cursor)
            self.wm_one.register_click_callback(
                lambda btn, is_down: self.dw.on_click())
            self.wm_one.register_confirm_callback(self.dw.save_highscore)
            self.wm_two = devices[1]
            self.wm_two.register_move_callback(self.dw.set_cursor)
            self.wm_two.register_click_callback(
                lambda btn, is_down: self.dw.on_click())
            self.wm_two.register_confirm_callback(self.dw.save_highscore)

    def highscore_chart(self):
        print('In Highscore Chart!')
        self.img = QtGui.QPixmap(self.imagePath)
        # TODO: Insert real score
        # TODO: abfangen ob es einen neuen score gibt oder der aufruf vom menü kommt
        self.score_pair.append([self.new_score, self.img])
        print('Score Pair nach append: ', self.score_pair)
        sorted_hs_list = sorted(self.highscore_list,
                                key=itemgetter(0), reverse=True)
        if self.score_pair[0][0] > sorted_hs_list[-1][0]:
            new_hs_list = self.set_highscores()
            self.draw_highscores(new_hs_list)
        else:
            self.draw_highscores(self.highscore_list)

    # Appends new score to highscore list
    def set_highscores(self):
        sorted_hs_list = sorted(self.highscore_list,
                                key=itemgetter(0), reverse=True)
        if len(sorted_hs_list) == 10 and sorted_hs_list[-1][0] < self.score_pair[0][0]:
            del sorted_hs_list[-1]
            sorted_hs_list.append(self.score_pair[0])
        else:
            sorted_hs_list.append(self.score_pair[0])
        return sorted_hs_list

    # Draws Table with highscores
    def draw_highscores(self, actual_list):
        new_list = sorted(actual_list, key=itemgetter(0), reverse=True)
        self.highscore_table.setRowCount(10)
        self.highscore_table.setColumnCount(2)
        self.highscore_table.setHorizontalHeaderLabels(['Name', 'Score'])
        i = 0
        for item in new_list:
            actual_score = item[0]
            if type(item[1]) is not str:
                sign_to_icon = QtGui.QIcon(QtGui.QPixmap(item[1]))
                new_sign_entry = QtWidgets.QTableWidgetItem(sign_to_icon, "")
                self.highscore_table.setItem(i, 0, new_sign_entry)
            elif type(item[1]) is str:
                sign_placeholder = QtWidgets.QTableWidgetItem(item[1])
                self.highscore_table.setItem(i, 0, sign_placeholder)

            new_score_entry = QtWidgets.QTableWidgetItem(str(actual_score))
            self.highscore_table.setItem(i, 1, new_score_entry)
            self.highscore_table.setRowHeight(i, 60)
            i += 1

        self.highscore_table.setIconSize(self.icon_size)
        self.highscore_table.resize(300, 500)
        self.highscore_list = new_list


class DrawWidget(QtWidgets.QWidget):

    # pyqtsignal for the recognition at the end of each drawing interaction
    finished_unistroke = QtCore.pyqtSignal(object, bool, str)

    def __init__(self):
        super(DrawWidget, self).__init__()
        self.width = 1000
        self.height = 1000
        self.setMouseTracking(True)
        self.recognize_flag = False
        self.click_flag = False
        self.positions = []
        self.path = QtGui.QPainterPath()
        self.bt_save = QtWidgets.QPushButton(parent=self)
        self.instruction = QtWidgets.QLabel(parent=self)
        self.init_ui()
        self.flag = False
        self.t_name = ""
        self.save_callback = None

    def init_ui(self):
        self.setWindowTitle("Signature")
        self.setGeometry(0, 0, self.width, self.height)
        self.setAutoFillBackground(True)
        layout = QtWidgets.QVBoxLayout(self)

        self.bt_save.setText('Save Highscore')
        self.bt_save.setFixedSize(120, 30)
        self.bt_save.clicked.connect(self.save_highscore)
        layout.addWidget(self.bt_save)
        self.instruction.setText('Click and hold "B" for drawing'
                                 'Release "B" when you are ready'
                                 'Confirm with "A')
        # self.instruction.move(130, 250)
        layout.addWidget(self.instruction, alignment=QtCore.Qt.AlignTop)
        self.setLayout(layout)
        self.show()

    def set_callback(self, callback):
        self.save_callback = callback

    def save_highscore(self):
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
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setPen(QtGui.QPen(QtCore.Qt.black, 7, QtCore.Qt.SolidLine))
        qp.drawPath(self.path)
        qp.end()

    # callback function for the button press and release event
    # Toggle funcitonality by
    # https://stackoverflow.com/questions/8381735/how-to-toggle-a-value-in-python
    # Pyqtsignal emitting
    def on_click(self):
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


# class HighscoreHandler():
    # def __init__(self):
       # super(HighscoreHandler, self).__init__()
        # self.hs = HighscoreWidget(43)
        # self.dw = DrawWidget()
        # self.dw.set_callback(self.hs.highscore_chart)
