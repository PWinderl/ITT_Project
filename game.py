from PyQt5 import QtWidgets, QtCore, Qt
import sys
import pygame
from threading import Thread

CUSTOMEVENT = pygame.USEREVENT+1


class GameController():

    def __init__(self, width, height):
        self.size = width, height
        self.screen = pygame.display.set_mode(self.size)
        self.init_ui()
        self.clock = pygame.time.Clock()
        self.rects = []

    def init_ui(self):
        step = self.size[0] / 8
        pygame.draw.line(self.screen, (255, 255, 255),  [
                         step * 0, 0], [step * 0, self.size[1]], 5)
        pygame.draw.line(self.screen, (255, 255, 255),  [
                         step * 1, 0], [step * 1, self.size[1]], 5)
        pygame.draw.line(self.screen, (255, 255, 255),  [
                         step * 2, 0], [step * 2, self.size[1]], 5)
        pygame.draw.line(self.screen, (255, 255, 255),  [
                         step * 3, 0], [step * 3, self.size[1]], 5)
        pygame.draw.line(self.screen, (255, 255, 255),  [
                         step * 4, 0], [step * 4, self.size[1]], 5)
        pygame.display.update()

    def run(self):
        while 1:
            for event in pygame.event.get():
                if event.type == CUSTOMEVENT:
                    try:
                        self.rects.append(
                            {"size": event.dict["size"], "line": event.dict["line"], "speed": event.dict["speed"]})
                    except Exception as e:
                        print(e)
                if event.type == pygame.QUIT:
                    sys.exit()

            for item in self.rects:
                if "rect" not in item:
                    rect = item["rect"] = pygame.draw.rect(
                        self.screen, (0, 0, 0), self.get_pos_and_size(item["line"], item["size"]))
                else:
                    rect = item["rect"]
                pygame.draw.rect(self.screen, (0, 0, 0), rect)
                pygame.display.update(rect)
                rect = rect.move(0, 1)
                rect = pygame.draw.rect(
                    self.screen, (255, 255, 255), rect)
                if rect.top >= 1000:
                    self.rects.remove(item)
                else:
                    item["rect"] = rect
                    self.rects[self.rects.index(item)] = item

                # needs to run in every loop
                pygame.display.update(rect)
                self.clock.tick(30)
        pygame.quit()

    def get_pos_and_size(self, line, size):
        return [
            (self.size[0] / 8) * line + (self.size[0] / 16) - 10, 0, size[0], size[1]]


class Game(Thread):

    def __init__(self, width, height):
        super().__init__()
        self.controller = GameController(width, height)

    def run(self):
        self.controller.run()


class GameEvent():

    def __init__(self):
        self.callbacks = []

    def register_callback(self, callback):
        self.callbacks.append(callback)

    def call(self, event):
        for callback in self.callbacks:
            callback(event)

    def fire(self, event, data):
        pygame.event.post(pygame.event.Event(event, data))


Game(1920, 1080).start()
GameEvent().fire(CUSTOMEVENT, {"size": (20, 20), "line": 0, "speed": 30})
GameEvent().fire(CUSTOMEVENT, {"size": (20, 20), "line": 2, "speed": 30})
