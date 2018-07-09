from PyQt5 import QtWidgets, QtCore, QtGui
import sys
from recognizer import Recognizer


class DrawWidget(QtWidgets.QWidget):

    # pyqtsignal for the recognition at the end of each drawing interaction
    finished_unistroke = QtCore.pyqtSignal(object, bool, str)

    def __init__(self, name, x, y, width, height):
        super(DrawWidget, self).__init__()
        self.width = width
        self.height = height
        self.setMouseTracking(True)
        self.recognize_flag = False
        self.click_flag = False
        self.positions = []
        self.path = QtGui.QPainterPath()
        self.init_ui(name, x, y, width, height)
        self.name = name

    def init_ui(self, name, x, y, width, height):
        self.setWindowTitle("DrawingBoard of " + name)
        self.setGeometry(x, y, width, height)
        self.setAutoFillBackground(True)
        self.show()
        self.setStyleSheet("background-color:white;")
        self.update()

    def set_cursor(self, x, y):
        QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(x, y)))

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
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
                self.positions, True, self.name)

    # on move callback for position update of wiimote
    def on_move(self, x, y):
        self.set_cursor(x, y)
        pos = QtCore.QPoint(x, y)
        if self.click_flag:
            self.click_flag = False
            self.path.moveTo(pos)
            self.positions.append((pos.x(), pos.y()))
            self.update()
            return
        self.positions.append((pos.x(), pos.y()))
        self.path.lineTo(pos)
        self.update()

    """
    This methods will not be needed.
    Just for testing.
    """

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
        self.finished_unistroke.emit(self.positions, True, self.name)
        self.positions = []

# TODO: Templates


class TemplateWidget(QtWidgets.QWidget):

    def __init__(self, x, y, width, height):
        super(TemplateWidget, self).__init__()
        self.width = width
        self.height = height
        self.init_ui(x, y, width, height)
        self.path = QtGui.QPainterPath()

    def init_ui(self, x, y, width, height):
        self.setWindowTitle("Template")
        self.setGeometry(x, y, width, height)
        self.setAutoFillBackground(True)
        self.show()

    # TODO: add points to path
    # pay attention to start point
    def draw(self, points):
        self.update()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPath(self.path)
        qp.end()


class MiniGame():

    def __init__(self, resolution, size):
        app = QtWidgets.QApplication(sys.argv)
        rec = Recognizer()
        player = DrawWidget("player",
                            0, resolution[1] / 2 - size[1] / 2, size[0], size[1])
        player.finished_unistroke.connect(rec.recognize)
        rec.set_callback(self.on_result)
        conductor = DrawWidget("conductor",
                               resolution[0] - size[0], resolution[1] / 2 - size[1] / 2, size[0], size[1])
        conductor.finished_unistroke.connect(rec.recognize)
        rec.set_callback(self.on_result)
        template = TemplateWidget(
            resolution[0] / 2 - size[0] / 2, resolution[1] / 2 - size[1] / 2, size[0], size[1])
        sys.exit(app.exec_())

    def on_result(self, template, score, name):
        print(name)
        print(score)
        print(template)


# 1920/975 my resolution
# find out with xdpyinfo | grep dimensions
MiniGame((1920, 975), (500, 500))
