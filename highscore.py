from PyQt5 import QtWidgets, QtCore, QtGui, Qt
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
        self.new_score = end_score
        self.highscore_table = QtWidgets.QTableWidget(10, 2, parent=self)
        self.highscore_table.setHorizontalHeaderLabels(['Name', 'Score'])
        self.highscore_table.horizontalHeader().setStretchLastSection(True)
        self.highscore_table.verticalHeader().setStretchLastSection(True)
        self.highscore_list = [[55, "Fabian"], [44, "Paul"], [66, "Thomas"], [44, "Paul"], [44, "Paul"], [44, "Paul"],
                               [44, "Paul"], [44, "Paul"], [44, "Paul"]]
        self.init_ui()

        # Check if highscore.py was started from menu or after game
        # In case of game show signature screen
        if self.new_score != 0:
            self.dw = DrawWidget()
            self.init_devices(devices)
            self.dw.set_callback(self.highscore_chart)
        else:
            self.draw_highscores(self.highscore_list)

    # Init UI: sets size and layout
    def init_ui(self):
        self.setFixedSize(300, self.height)
        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.highscore_table, 1, 1)
        self.setLayout(layout)
        self.show()

    # Registers Wiimote
    # Set callbacks for Wiimote
    def init_devices(self, devices):
        # if len(devices) == 1:
        self.wm_one = devices[0]
        self.wm_one.register_click_callback(
            lambda btn, is_down: self.dw.on_click())
        self.wm_one.register_confirm_callback(self.dw.save_highscore)
        # elif len(devices) == 2:
        #     self.wm_one = devices[0]
        #     self.wm_one.register_move_callback(self.dw.set_cursor)
        #     self.wm_one.register_click_callback(
        #         lambda btn, is_down: self.dw.on_click())
        #     self.wm_one.register_confirm_callback(self.dw.save_highscore)
        #     self.wm_two = devices[1]
        #     self.wm_two.register_move_callback(self.dw.set_cursor)
        #     self.wm_two.register_click_callback(
        #         lambda btn, is_down: self.dw.on_click())
        #     self.wm_two.register_confirm_callback(self.dw.save_highscore)

    # Fetch signature painting and translate to QPixmap
    # Connect new score with painted signature
    # Check if new score is high enough to append to highscore list
    def highscore_chart(self):
        self.img = QtGui.QPixmap(self.imagePath)
        self.score_pair.append([self.new_score, self.img])
        sorted_hs_list = sorted(self.highscore_list,
                                key=itemgetter(0), reverse=True)
        if self.score_pair[0][0] > sorted_hs_list[-1][0] or len(sorted_hs_list) < 10:
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
        i = 0
        for item in new_list:
            actual_score = item[0]
            if type(item[1]) is not str:
                sign_to_icon = QtGui.QIcon(QtGui.QPixmap(item[1]))
                new_sign_entry = QtWidgets.QTableWidgetItem(sign_to_icon, "")
                self.highscore_table.setItem(i, 0, new_sign_entry)
            elif type(item[1]) is str:
                sign_placeholder = QtWidgets.QTableWidgetItem(item[1])
                sign_placeholder.setBackground(QtCore.Qt.gray)
                self.highscore_table.setItem(i, 0, sign_placeholder)

            new_score_entry = QtWidgets.QTableWidgetItem(str(actual_score))
            if i % 2 == 0:
                new_score_entry.setBackground(QtCore.Qt.green)
            else:
                new_score_entry.setBackground(QtCore.Qt.blue)
            self.highscore_table.setItem(i, 1, new_score_entry)
            self.highscore_table.setRowHeight(i, 60)
            i += 1

        self.highscore_table.setIconSize(self.icon_size)

        self.highscore_list = new_list


class DrawWidget(QtWidgets.QWidget):

    # pyqtsignal for the recognition at the end of the drawing interaction
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

    # UI for signature drawing
    def init_ui(self):
        self.setWindowTitle("Signature")
        self.setGeometry(0, 0, self.width, self.height)
        self.setAutoFillBackground(True)
        layout = QtWidgets.QVBoxLayout(self)

        self.bt_save.setText('Save Highscore')
        self.bt_save.setFixedSize(120, 30)
        self.bt_save.clicked.connect(self.save_highscore)
        layout.addWidget(self.bt_save)
        self.instruction.setText('Click and hold "A" for drawing' + "\n" +
                                 'Release "A" when you are ready' + "\n" +
                                 'Confirm with "B"')
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