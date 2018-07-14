#!/usr/bin/env python3
# coding: utf-8

"""
By Thomas Oswald
"""

from PyQt5 import QtWidgets, QtCore, Qt
import sys
import pygame
import os

NOTE_INCOMING = pygame.USEREVENT + 1
PAUSE = pygame.USEREVENT + 2
CONTINUE = pygame.USEREVENT + 3
ACTION = pygame.USEREVENT + 4
HIT = pygame.USEREVENT + 5
EXIT = pygame.USEREVENT + 6

# TODO: notes destroy target, when no action_flag is set


class Game():

    def __init__(self, width, height):
        self.width, self.height = width, height
        # SET WINDOW POS
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100, 100)
        pygame.init()
        self.screen = pygame.display.set_mode((width, height), pygame.NOFRAME)
        self.circles = []
        self.init_ui()

    # part 1 lines: 0 - 1 | 1 - 2 | 2 - 3 | 3 - 4 |
    # part 2 lines: 8 - 9 | 9 - 10 | 10 - 11 | 11 - 12 |
    def init_ui(self):
        lines = 8 + 4
        line_size = self.width / lines
        step = 0
        color = (255, 255, 255)
        circle_radius = 40
        while step <= lines:
            if step == lines / 2:
                color = (100, 250, 115)
            if step < 4:
                x, y = (int((line_size * step + line_size *
                             (step + 1)) / 2) - circle_radius / 2, self.height - 50)
                self.circles.append(pygame.draw.ellipse(
                    self.screen, (255, 255, 255), (x, y, circle_radius, circle_radius)))
            pygame.draw.line(self.screen, color,  [
                line_size * step, 0], [line_size * step, self.height], 5)
            if step == lines / 3 or step == lines / 2:
                color = (255, 255, 255)
                step += 2
            else:
                step += 1

        pygame.display.update()

    def run(self):
        is_running = True
        pause_flag = False

        # for testing on True
        action_flag = True
        action_line = -1
        rects = []
        clock = pygame.time.Clock()
        white = (255, 255, 255)
        while is_running:
            for event in pygame.event.get():
                if event.type == NOTE_INCOMING:
                    try:
                        rects.append(
                            {"size": event.dict["size"],
                                "line": event.dict["line"],
                                "speed": event.dict["speed"],
                                "screen": event.dict["screen"]})
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
                    pygame.display.flip()
                    pause_flag = True
                if event.type == CONTINUE:
                    screen = pygame.display.set_mode(
                        (self.width, self.height), pygame.NOFRAME)
                    screen.blit(pygame.transform.scale(
                        self.screen, (self.width, self.height)), (0, 0))
                    self.screen = screen
                    pygame.display.flip()
                    pause_flag = False
                if event.type == ACTION:
                    action_flag = True
                    action_line = event.dict["line"]
                if event.type == HIT:
                    for circle in self.circles:
                        self.change_ellipse_color(circle, white)
                    pygame.time.set_timer(HIT, 0)
                if event.type == EXIT:
                    is_running = False
                if event.type == pygame.QUIT:
                    sys.exit()
            if not pause_flag:
                for item in rects:
                    if "rect" not in item:
                        rect = item["rect"] = self.add_rect(item)
                    else:
                        rect = item["rect"]
                    self.remove_rect(rect)
                    rect = rect.move(0, 1)
                    rect = pygame.draw.rect(
                        self.screen, white, rect)
                    if item["screen"] == 1 and action_flag:
                        action_flag = False
                        if item["line"] == action_line:
                            target = self.circles[action_line]
                            if rect.colliderect(target):
                                self.remove_rect(rect)
                                self.rects.remove(item)
                                self.change_ellipse_color(
                                    target, (100, 250, 115))
                                pygame.time.set_timer(HIT, 100)

                    if rect.top >= self.height - rect.height:
                        self.remove_rect(rect)
                        rects.remove(item)
                        if item["screen"] == 2:
                            item["screen"] = 1
                            item["rect"] = self.add_rect(item)
                            rects.append(item)
                    else:
                        try:
                            item["rect"] = rect
                            rects[rects.index(item)] = item
                        except ValueError as e:
                            pass

                    # needs to run in every loop
                    pygame.display.update(rect)
                clock.tick(240)
        pygame.quit()

    # TODO: Extend this code
    def play_note(self):
        pygame.mixer.music.load("Sample.mp3")
        pygame.mixer.music.play()

    def change_ellipse_color(self, rect, color):
        ellipse = pygame.draw.ellipse(self.screen, color, rect)
        pygame.display.update(rect)
        return ellipse

    def remove_rect(self, rect):
        pygame.draw.rect(self.screen, (0, 0, 0), rect)
        pygame.display.update(rect)

    def add_rect(self, item):
        return pygame.draw.rect(self.screen, (0, 0, 0), self.get_pos_and_size(
            item["screen"], item["line"], item["size"]))

    def get_pos_and_size(self, screen, line, size):
        if screen == 2:
            line += 8
        width, height = size
        middle = (self.width / 12 * line + self.width / 12 * (line + 1)) / 2
        return [middle - width / 2, 0, width, height]


class GameController(QtCore.QThread):

    def __init__(self, width, height, parent=None):
        super(GameController, self).__init__(parent)
        self.game = Game(width, height)

    def run(self):
        self.game.run()


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

    def __init__(self, size, parent=None):
        super(GameWidget, self).__init__(parent)
        self.width, self.height = size
        self.init_ui()
        self.init_game()

    def init_ui(self):
        self.setFixedSize(self.width, self.height)
        self.show()

    def init_game(self):
        self.controller = GameController(
            self.width - 100, self.height - 100, parent=self).start()

        QtCore.QTimer.singleShot(500, self.test)
        QtCore.QTimer.singleShot(1000, self.test2)

    def test(self):
        pygame.event.post(pygame.event.Event(PAUSE))

    def test2(self):
        pygame.event.post(pygame.event.Event(CONTINUE))


"""
event = GameEvent(NOTE_INCOMING)
Game(1920, 800).start()
event.emit({"size": (20, 20),
            "line": 0, "speed": 30, "screen": 1})
event.emit({"size": (20, 20),
            "line": 1, "speed": 30, "screen": 2})
pygame.event.post(pygame.event.Event(PAUSE))
pygame.event.post(pygame.event.Event(CONTINUE))


def emit():
    event.emit({"size": (20, 20),
                "line": 0, "speed": 30, "screen": 1})


# d = SetupBluetooth(1)
# d1.register_click_callback(emit)
"""
