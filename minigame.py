#!/usr/bin/env python3
# coding: utf-8

"""
By Thomas Oswald
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import sys
from recognizer import Recognizer
from random import randint
# from bluetooth_input import SetupBluetooth


class DrawWidget(QtWidgets.QFrame):

    # pyqtsignal for the recognition at the end of each drawing interaction
    finished_unistroke = QtCore.pyqtSignal(object, bool, str)

    def __init__(self, name, width, height, parent=None):
        super(DrawWidget, self).__init__(parent)
        self.width = width
        self.height = height
        self.setMouseTracking(True)
        self.recognize_flag = False
        self.click_flag = False
        self.positions = []
        self.path = QtGui.QPainterPath()
        self.init_ui(name, width, height)
        self.name = name

    def init_ui(self, name, width, height):
        self.setWindowTitle("DrawingBoard of " + name)
        self.setAutoFillBackground(True)
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFixedSize(width, height)
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


class TemplateWidget(QtWidgets.QFrame):

    def __init__(self, width, height, parent=None):
        super(TemplateWidget, self).__init__(parent)
        self.width = width
        self.height = height
        self.init_ui(width, height)
        self.path = QtGui.QPainterPath()
        template = self.get_random_template().split(":")
        self.t_name = template[0]
        self.draw(eval(template[1]))

    def init_ui(self, width, height):
        self.setWindowTitle("Template")
        self.setFixedSize(width, height)
        self.setAutoFillBackground(True)

    # TODO: points need to be a accurate in the center
    def draw(self, points):
        center = (200, 200)
        self.path.moveTo(points[0][0] + center[0],
                         points[0][1] + center[0])
        for point in points[1:]:
            self.path.lineTo(point[0] + center[0],
                             point[1] + center[0])
        self.update()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPath(self.path)
        qp.end()

    def get_random_template(self):
        lines = []
        with open("strokes.map", "r") as strokes:
            lines = strokes.readlines()
        if len(lines) > 0:
            return lines[randint(0, len(lines) - 1)]
        return None


class MiniGameWidget(QtWidgets.QWidget):

    def __init__(self, size, devices, b_player=None, b_conductor=None, parent=None):
        super(MiniGameWidget, self).__init__(parent)
        self.showFullScreen()
        rec = Recognizer()
        rec.set_callback(self.on_result)

        layout = QtWidgets.QHBoxLayout(self)

        player = DrawWidget("player", size[0], size[1], self)

        player.finished_unistroke.connect(rec.recognize)

        layout.addWidget(player, alignment=QtCore.Qt.AlignLeft)

        template = TemplateWidget(size[0], size[1], self)

        layout.addWidget(template, alignment=QtCore.Qt.AlignCenter)

        conductor = DrawWidget("conductor", size[0], size[1], self)

        conductor.finished_unistroke.connect(rec.recognize)

        layout.addWidget(conductor, alignment=QtCore.Qt.AlignRight)

        button = QtWidgets.QPushButton(self)
        layout.addWidget(button)

        self.setLayout(layout)

        self.connect_wms(player, conductor)
        template.show()
        player.show()
        conductor.show()
        self.show()

    def connect_wms(self, player, conductor):
        """
        d1 = SetupBluetooth(1)
        d2 = SetupBluetooth(2)

        d1.register_click_callback(player.on_click)
        d1.register_move_callback(player.on_move)
        d2.register_click_callback(conductor.on_click)
        d2.register_move_callback(conductor.on_move)
        """
        # connect to input of player wiimote
        # player.on_click.connect()
        # player.on_move.connect()

        # connect to input of conductor wiimote
        # conductor.on_click.connect()
        # conductor.on_move.connect()

    def on_result(self, template, score, name):
        print(name)
        # print(score)
        # print(template)


# 1920/975 my resolution
# find out with xdpyinfo | grep dimensions
