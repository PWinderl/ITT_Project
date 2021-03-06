#!/usr/bin/env python3
# coding: utf-8

"""
The Minigame module consists of three widgets on a parent widget.
Two of them are DrawWidgets, which are used to let the players draw unistrokes.
The third is the TemplateWidget. It will show a template, which the players need to draw.

Author: Thomas Oswald
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from recognizer import Recognizer
from random import randint
from bt_input import Device


class DrawWidget(QtWidgets.QFrame):

    """
    The DrawWidget is responsible for displaying an area in which the users can draw.
    """

    # pyqtsignal for the recognition at the end of each drawing interaction
    finished_unistroke = QtCore.pyqtSignal(object, str, str)

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
        self.just_started = False
        self.t_name = ""

    def init_ui(self, name, width, height):
        self.setAutoFillBackground(True)
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFixedSize(width, height)
        self.setStyleSheet(
            "background-color:white; border:1px solid rgb(0, 0, 0);")
        self.cursor_pos = QtCore.QPoint(width / 2, height / 2)
        self.update()

    def set_cursor(self, point):
        self.cursor_pos = point

    def draw_cursor(self, qp):
        if self.cursor_pos is not None:
            qp.drawEllipse(self.cursor_pos, self.cursor_radius,
                           self.cursor_radius)

    # Overwritten method responsible for painting
    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPath(self.path)
        self.draw_cursor(qp)
        qp.end()

    def on_template_selected(self, t_name):
        self.t_name = t_name

    # callback function for the button press and release event
    # Pyqtsignal emitting
    def on_click(self, btn, is_down):
        if btn == Device.BTN_A:
            self.click_flag = not self.click_flag
            self.just_started = True
            if not self.click_flag:
                print("emitted")
                self.finished_unistroke.emit(
                    self.positions, self.name, self.t_name)

    # on move callback for position update of wiimote
    def on_move(self, x, y):
        if self.click_flag:
            pos = QtCore.QPoint(x, y)  # self.mapToGlobal(QtCore.QPoint(x, y))
            self.set_cursor(pos)
            if self.just_started:
                self.just_started = False
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

    TODO: DELETE
    

    # mouse moves with mouse or with set_cursor
    def mouseMoveEvent(self, event):
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
        self.path.moveTo(event.pos())
        self.update()

    def mouseReleaseEvent(self, event):
        self.finished_unistroke.emit(self.positions, self.name, self.t_name)
        self.positions = []
    """


class TemplateWidget(QtWidgets.QFrame):

    """
    The TemplateWidget will randomly show a unistroke painting at the start of the minigame.
    """

    template_selected = QtCore.pyqtSignal(str)

    def __init__(self, width, height, parent=None):
        super(TemplateWidget, self).__init__(parent)
        self.width = width
        self.height = height
        self.init_ui(width, height)
        self.path = QtGui.QPainterPath()

    def init_ui(self, width, height):
        self.setStyleSheet(
            "background-color:white; border:1px solid rgb(0, 0, 0);")
        self.setFixedSize(width, height)
        self.setAutoFillBackground(True)

    # This function draws a random template in the widget.
    def draw(self):
        template = self.get_random_template().split(":")
        t_name = template[0]
        points = eval(template[1])
        self.template_selected.emit(t_name)

        center = (self.width / 2, self.height / 2)
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

    # This method selects a template randomly.
    def get_random_template(self):
        lines = []
        with open("strokes.map", "r") as strokes:
            lines = strokes.readlines()
        if len(lines) > 0:
            return lines[randint(0, len(lines) - 1)]
        return None


class MiniGameWidget(QtWidgets.QWidget):

    """
    The MiniGameWidget is the parent of the three other widgets.
    It coordinates them and connects the bluetooth input to the DrawWidgets.
    After the two players drew the line, each of those will be moved to a $1 recognition algorithm.
    The unistroke, which is the closest to the template,
    will be recognized and as such the user will win the minigame.
    """

    on_end = QtCore.pyqtSignal(str)

    def __init__(self, size, devices, parent=None):
        super(MiniGameWidget, self).__init__(parent)
        self.width, self.height = size
        self.scores = []
        self.player, self.conductor, self.template = self.init_ui()
        rec_1 = Recognizer()
        rec_2 = Recognizer()
        rec_1.set_callback(self.on_result)
        rec_2.set_callback(self.on_result)

        self.template.template_selected.connect(
            self.player.on_template_selected)
        self.template.template_selected.connect(
            self.conductor.on_template_selected)
        self.player.finished_unistroke.connect(
            lambda points, name, t_name: self.on_rec(rec_1, points, name, t_name))
        self.conductor.finished_unistroke.connect(
            lambda points, name, t_name: self.on_rec(rec_2, points, name, t_name))

        self.devices = None
        if devices is not None and len(devices) > 0:
            self.connect_devices(devices, self.player, self.conductor)
            self.devices = devices
        self.template.show()
        self.player.show()
        self.conductor.show()
        self.show()
        self.setHidden(False)

        self.template.draw()

    def hide(self):
        if self.devices is not None:
            for device in self.devices:
                device.unregister_callbacks()
        self.template.setParent(None)
        self.player.setParent(None)
        self.conductor.setParent(None)
        self.setHidden(True)
        self.close()

    def init_ui(self):
        self.showFullScreen()

        layout = QtWidgets.QHBoxLayout(self)

        player = DrawWidget("player", self.width, self.height, self)
        layout.addWidget(player, alignment=QtCore.Qt.AlignLeft)

        template = TemplateWidget(self.width, self.height, self)
        layout.addWidget(template, alignment=QtCore.Qt.AlignCenter)

        conductor = DrawWidget("conductor", self.width, self.height, self)
        layout.addWidget(conductor, alignment=QtCore.Qt.AlignRight)

        self.setLayout(layout)

        return (player, conductor, template)

    def on_rec(self, rec, points, name, t_name):
        print("begin rec")
        rec.recognize(points, name, t_name)

    # This method gets the result of the recognition processes.
    # After receiving two results, it will decide who won.
    def on_result(self, template, score, name):
        print("received result")
        self.scores.append({"name": name, "score": score})
        if len(self.scores) > 1:
            if abs(self.scores[0]["score"]) < abs(self.scores[1]["score"]):
                self.on_end.emit(self.scores[0]["name"])
            else:
                self.on_end.emit(self.scores[1]["name"])

    def connect_devices(self, devices, player, conductor):
        if len(devices) > 0:
            devices[0].register_click_callback(player.on_click)
            devices[0].register_move_callback(player.on_move)
        if len(devices) > 1:
            devices[1].register_click_callback(conductor.on_click)
            devices[1].register_move_callback(conductor.on_move)
