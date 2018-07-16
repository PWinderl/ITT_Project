#!/usr/bin/env python3
# coding: utf-8

"""
By Thomas Oswald
"""

from PyQt5 import QtWidgets, QtCore, Qt
import sys
import pygame
import os
# For testing
import traceback

NOTE_INCOMING = pygame.USEREVENT + 1
PAUSE = pygame.USEREVENT + 2
CONTINUE = pygame.USEREVENT + 3
ACTION = pygame.USEREVENT + 4
HIT = pygame.USEREVENT + 5
FAIL = pygame.USEREVENT + 6
EXIT = pygame.USEREVENT + 7

# TODO: notes destroy target, when no action_flag is set


class Game():

    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (100, 250, 115)
    BLUE = (51, 0, 255)

    CUBE_FACTOR = 0.2
    CIRCLE_FACTOR = 0.3
    TARGET_Y_FACTOR = 0.1

    def __init__(self, res):
        # SET WINDOW POS
        width, height = res
        self.width = int(width * 0.8)
        self.height = int(height * 0.8)
        print(width, height, self.width, self.height)
        frame_x = (width - self.width) / 2
        frame_y = (height - self.height) / 2
        print(frame_x, frame_y)
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (frame_x, frame_y)

        # 8 lines and 4 for spacing between screens
        self.lines = 8 + 4
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.width, self.height), pygame.NOFRAME)
        self.circles = []
        self.rects = []
        self.init_ui(self.screen, self.width, self.height)

    # part 1 lines: 0 - 1 | 1 - 2 | 2 - 3 | 3 - 4 |
    # part 2 lines: 8 - 9 | 9 - 10 | 10 - 11 | 11 - 12 |
    def init_ui(self, screen, width, height):
        line_size = width / self.lines
        step = 0
        color = self.WHITE
        circle_radius = line_size * self.CIRCLE_FACTOR
        circle_y = height * self.TARGET_Y_FACTOR
        while step <= self.lines:
            if step == self.lines / 2:
                color = self.GREEN
            if step < 4:
                x, y = (int((line_size * step + line_size *
                             (step + 1)) / 2) - circle_radius / 2, height - circle_y)
                self.circles.append(pygame.draw.ellipse(
                    screen, self.BLUE, (x, y, circle_radius, circle_radius)))
            pygame.draw.line(screen, color,  [
                line_size * step, 0], [line_size * step, height], 5)
            if step == self.lines / 3 or step == self.lines / 2:
                color = self.WHITE
                step += 2
            else:
                step += 1

        pygame.display.flip()

    def redraw(self, screen, width, height):
        self.init_ui(screen, width, height)
        for item in self.rects:
            if "rect" in item:
                ratio_y = item["rect"].y / self.width
                new_y = width * ratio_y
                item["rect"] = self.create_cube(screen, item, width, new_y)
                self.rects[self.rects.index(item)] = item

    def run(self):
        is_running = True
        pause_flag = False

        clock = pygame.time.Clock()

        frame_rate = 60
        while is_running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                if event.type == NOTE_INCOMING:
                    try:
                        self.rects.append(
                            {"speed": frame_rate / 2,
                                "line": event.dict["line"],
                                "field": event.dict["field"]})
                    except Exception as e:
                        print(e)
                # Used for hiding and showing:
                # https://stackoverflow.com/questions/34910086/pygame-how-do-i-resize-a-
                # surface-and-keep-all-objects-within-proportionate-to-t
                if event.type == PAUSE:
                    screen = pygame.display.set_mode(
                        (300, 300), pygame.NOFRAME)
                    screen.blit(pygame.transform.scale(
                        self.screen, (300, 300)), (0, 0))
                    self.redraw(screen, 300, 300)
                    pygame.display.flip()
                    pause_flag = True
                if event.type == CONTINUE:
                    screen = pygame.display.set_mode(
                        (self.width, self.height), pygame.NOFRAME)
                    screen.blit(pygame.transform.scale(
                        self.screen, (self.width, self.height)), (0, 0))
                    self.screen = screen
                    self.redraw(self.screen, self.width, self.height)
                    pygame.display.flip()
                    pause_flag = False
                if event.type == ACTION:
                    print("Is hit:", self.is_hit(event.dict["line"]))
                if event.type == HIT:
                    for circle in self.circles:
                        self.change_ellipse_color(circle, self.BLUE)
                    pygame.time.set_timer(HIT, 0)
                if event.type == FAIL:
                    for circle in self.circles:
                        self.change_ellipse_color(circle, self.BLUE)
                    pygame.time.set_timer(FAIL, 0)
                if event.type == EXIT:
                    is_running = False
                if event.type == pygame.QUIT:
                    sys.exit()
            if not pause_flag:
                for item in self.rects:
                    # moving rect
                    if "rect" not in item:
                        rect = item["rect"] = self.create_cube(
                            self.screen, item, self.width)
                    else:
                        rect = item["rect"]
                    self.remove_rect(rect)
                    rect = rect.move(0, 1)
                    rect = pygame.draw.rect(
                        self.screen, self.WHITE, rect)

                    # change game field (conductor -> player)
                    if rect.top >= self.height - rect.height:
                        self.remove_rect(rect)
                        self.rects.remove(item)
                        if item["field"] == 2:
                            item["field"] = 1
                            item["rect"] = self.add_rect(item)
                            self.rects.append(item)
                    else:
                        try:
                            item["rect"] = rect
                            self.rects[self.rects.index(item)] = item
                        except ValueError as e:
                            pass

                    # needs to run in every loop
                    pygame.display.update(rect)
                clock.tick(frame_rate)
        pygame.quit()

    # TODO: Extend this code
    def play_note(self):
        pygame.mixer.music.load("Sample.mp3")
        pygame.mixer.music.play()

    def is_hit(self, line):
        for item in self.rects:
            if "rect" in item:
                rect = item["rect"]
                target = self.circles[line]
                if item["field"] == 1 and item["line"] == line and rect.colliderect(target):
                    self.remove_rect(rect)
                    self.rects.remove(item)
                    self.change_ellipse_color(
                        target, self.GREEN)
                    pygame.time.set_timer(HIT, 100)
                    return True
                else:
                    self.change_ellipse_color(
                        target, self.RED)
                    pygame.time.set_timer(FAIL, 100)
        return False

    def change_ellipse_color(self, rect, color):
        ellipse = pygame.draw.ellipse(self.screen, color, rect)
        pygame.display.update(rect)
        return ellipse

    def remove_rect(self, rect):
        pygame.draw.rect(self.screen, (0, 0, 0), rect)
        pygame.display.update(rect)

    def create_cube(self, screen, item, window_width, pre_pos_y=None):
        line = item["line"]
        field = item["field"]
        if field == 2:
            line += 8

        # get position and size of a cuboid
        # side = width and height of cuboid
        side = window_width / self.lines * self.CUBE_FACTOR
        middle = (window_width / self.lines * line +
                  window_width / self.lines * (line + 1)) / 2
        pos_y = 0
        if pre_pos_y is not None:
            pos_y = pre_pos_y
        return pygame.draw.rect(screen, self.WHITE, [middle - side / 2, pos_y, side, side])


class GameController(QtCore.QThread):

    def __init__(self, res, parent=None):
        super(GameController, self).__init__(parent)
        self.game = Game(res)

    def run(self):
        try:
            self.game.run()
        except Exception as e:
            # TODO: video system not initialized
            print(traceback.format_exc())
            print(e)


class GameEvent():

    def __init__(self, event):
        self.event = event
        self.callbacks = []

    def register_callback(self, callback):
        self.callbacks.append(callback)

    def call(self, data):
        for callback in self.callbacks:
            callback(data)

    def emit(self, data={}):
        pygame.event.post(pygame.event.Event(self.event, data))


class GameWidget(QtWidgets.QWidget):

    def __init__(self, resolution, devices, parent=None):
        super(GameWidget, self).__init__(parent)
        self.res = resolution
        self.is_pause = False
        self.player = None
        self.conductor = None

        self.init_ui()
        self.init_devices(devices)
        self.init_game()

    def init_ui(self):
        width = self.res[0] * 0.9
        height = self.res[1] * 0.9
        self.setFixedSize(width, height)

        layout = QtWidgets.QHBoxLayout(self)

        self.points_player = QtWidgets.QLabel("Points", parent=self)
        layout.addWidget(self.points_player, alignment=QtCore.Qt.AlignTop)

        self.points_conductor = QtWidgets.QLabel("Points", parent=self)
        layout.addWidget(self.points_conductor, alignment=QtCore.Qt.AlignTop)

        self.setLayout(layout)
        self.show()

    def init_devices(self, devices):
        if len(devices) > 0:
            self.player = devices[0]
            self.player.register_click_callback(
                lambda btn, is_down: self.on_button("player", btn, is_down))
            if len(devices) > 1:
                self.conductor = devices[1]

    def init_game(self):
        self.controller = GameController(self.res, parent=self).start()
        try:
            QtCore.QTimer.singleShot(
                500, lambda: self.on_button("conductor", 1, True))
            QtCore.QTimer.singleShot(2000, self.on_pause)
            QtCore.QTimer.singleShot(4000, self.on_continue)
        except Exception as e:
            print(traceback.format_exc())

    def on_button(self, char, btn, is_down):
        if not self.is_pause and is_down:
            if char == "player":
                pygame.event.post(pygame.event.Event(
                    ACTION, {"line": btn - 1}))
            elif char == "conductor":
                pygame.event.post(pygame.event.Event(
                    NOTE_INCOMING, {"line": btn - 1, "field": 2}))

    def on_pause(self):
        pygame.event.post(pygame.event.Event(PAUSE))
        self.is_pause = True

    def on_continue(self):
        pygame.event.post(pygame.event.Event(CONTINUE))
        self.is_pause = False
