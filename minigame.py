#!/usr/bin/env python3
# coding: utf-8

"""
By Thomas Oswald
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import sys
from recognizer import Recognizer
from random import randint
from bt_input import Device


class DrawWidget(QtWidgets.QFrame):

    # pyqtsignal for the recognition at the end of each drawing interaction
    finished_unistroke = QtCore.pyqtSignal(object, str)

    def __init__(self, name, width, height, parent=None):
        super(DrawWidget, self).__init__(parent)
        self.width = width
        self.height = height
        self.setMouseTracking(True)
        self.recognize_flag = False
        self.click_flag = False
        self.positions = []
        self.cursor_radius = 10
        self.cursor_pos = None
        self.path = QtGui.QPainterPath()
        self.init_ui(name, width, height)
        self.name = name

    def init_ui(self, name, width, height):
        self.setWindowTitle("DrawingBoard of " + name)
        self.setAutoFillBackground(True)
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFixedSize(width, height)
        self.setStyleSheet("background-color:white;")
        self.cursor_pos = QtCore.QPoint(width / 2, height / 2)
        self.update()

    def set_cursor(self, x, y):
        # QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(x, y)))
        self.cursor_pos = self.mapToGlobal(QtCore.QPoint(x, y))

    def draw_cursor(self, qp):
        if self.cursor_pos is not None:
            qp.drawEllipse(self.cursor_pos, self.cursor_radius,
                           self.cursor_radius)

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPath(self.path)
        self.draw_cursor(qp)
        qp.end()

    # callback function for the button press and release event
    # Toggle funcitonality by
    # https://stackoverflow.com/questions/8381735/how-to-toggle-a-value-in-python
    # Pyqtsignal emitting
    def on_click(self):
        # self.recognize_flag ^= True
        self.begin = True
        if not self.click_flag:
            self.finished_unistroke.emit(
                self.positions, self.name)

    # on move callback for position update of wiimote
    def on_move(self, x, y):
        self.set_cursor(x, y)
        pos = QtCore.QPoint(x, y)
        print("on move")
        print(self.click_flag)
        if self.begin:
            self.begin = False
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

    on_end = QtCore.pyqtSignal(str)

    def __init__(self, size, devices, b_player=None, b_conductor=None, parent=None):
        super(MiniGameWidget, self).__init__(parent)
        self.showFullScreen()
        rec_1 = Recognizer()
        rec_2 = Recognizer()
        rec_1.set_callback(self.on_result)
        rec_2.set_callback(self.on_result)

        layout = QtWidgets.QHBoxLayout(self)

        player = DrawWidget("player", size[0], size[1], self)

        player.finished_unistroke.connect(lambda points, name: self.on_rec(rec_1, points, name))

        layout.addWidget(player, alignment=QtCore.Qt.AlignLeft)

        template = TemplateWidget(size[0], size[1], self)

        layout.addWidget(template, alignment=QtCore.Qt.AlignCenter)

        conductor = DrawWidget("conductor", size[0], size[1], self)

        conductor.finished_unistroke.connect(lambda points, name: self.on_rec(rec_2, points, name))

        layout.addWidget(conductor, alignment=QtCore.Qt.AlignRight)

        self.setLayout(layout)

        if devices is not None and len(devices) > 0:
            self.connect_devices(devices, player, conductor)
        template.show()
        player.show()
        conductor.show()
        self.show()
    
    def on_rec(self, rec, points, name):
        rec.recognize(points, name)

    def connect_devices(self, devices, player, conductor):
        devices[0].register_confirm_callback(player.on_click)
        devices[0].register_move_callback(player.on_move)
        if len(devices) > 1:
            devices[1].register_confirm_callback(conductor.on_click)
            devices[1].register_move_callback(conductor.on_move)

    def on_result(self, template, score, name):
        print(name, "won")
        self.on_end.emit(name)
