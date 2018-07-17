#!/usr/bin/env python3
# coding: utf-8

"""
By Thomas Oswald
"""

from PyQt5 import QtWidgets, QtCore, Qt, QtGui
import sys
import pygame
import os
import time
# For testing
import traceback

NOTE_INCOMING = pygame.USEREVENT + 1
PAUSE = pygame.USEREVENT + 2
CONTINUE = pygame.USEREVENT + 3
ACTION = pygame.USEREVENT + 4
CLEAR_TARGET = pygame.USEREVENT + 5
EXIT = pygame.USEREVENT + 6
CLEAR_MUSIC = pygame.USEREVENT + 7


class GameThread(QtCore.QThread):

    on_hit = QtCore.pyqtSignal()
    on_fail = QtCore.pyqtSignal()
    on_end = QtCore.pyqtSignal()

    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (100, 250, 115)
    BLUE = (51, 0, 255)

    RECT_FACTOR = 0.2
    TARGET_FACTOR = 0.3
    TARGET_Y_FACTOR = 0.1

    TARGETS = [["sprites/a_inactive.png", "sprites/a_fail.png", "sprites/a_success.png"],
               ["sprites/b_inactive.png", "sprites/b_fail.png",
                   "sprites/b_success.png"],
               ["sprites/one_inactive.png", "sprites/one_fail.png",
                   "sprites/one_success.png"],
               ["sprites/two_inactive.png", "sprites/two_fail.png", "sprites/two_success.png"]]

    SOUNDS = ["sounds/violin_c.mp3", "sounds/violin_f.mp3",
              "sounds/violin_g.mp3", "sounds/violin_a.mp3"]

    def __init__(self, res, parent=None):
        super(GameThread, self).__init__(parent)
        # SET WINDOW POS
        self.res = res
        width, height = res
        self.width = int(width * 0.5)
        self.height = int(height * 0.5)
        self.center_position(self.width, self.height)

        # size of pause window
        self.p_width, self.p_height = (300, 300)

        # 8 lines and 4 for spacing between screens
        self.lines = 8 + 4
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.width, self.height), pygame.NOFRAME)
        self.circles = []
        self.rects = []
        self.background = self.init_background(self.screen)

    def center_position(self, width, height):
        full_width, full_height = self.res
        frame_x = (full_width - width) / 2
        frame_y = (full_height - height) / 2
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (frame_x, frame_y)

    # part 1 lines: 0 - 1 | 1 - 2 | 2 - 3 | 3 - 4 |
    # part 2 lines: 8 - 9 | 9 - 10 | 10 - 11 | 11 - 12 |
    def init_background(self, screen):
        width, height = screen.get_size()
        background = pygame.Surface((width, height))
        background = background.convert()
        background.fill((0, 0, 0))
        line_size = width / self.lines
        step = 0
        color = self.WHITE

        while step <= self.lines:
            if step == self.lines / 2:
                color = self.GREEN

            pygame.draw.line(background, color,  [
                line_size * step, 0], [line_size * step, height], 5)
            if step == self.lines / 3 or step == self.lines / 2:
                color = self.WHITE
                step += 2
            else:
                step += 1
        return background

    def init_targets(self):
        line_size = self.width / self.lines
        radius = int(line_size * self.TARGET_FACTOR)
        target_y = self.height - (self.height * self.TARGET_Y_FACTOR)
        group = pygame.sprite.Group()
        for step in range(4):
            x, y = (int((line_size * step + line_size *
                         (step + 1)) / 2) - radius / 2, target_y)
            group.add(Target(step, x, y, radius,
                             self.TARGETS[step], self.SOUNDS[step]))
        return group

    def redraw(self, screen, width, height):
        self.background = self.init_background(screen)
        for sprite in self.note_sprites.sprites():
            ratio_y = sprite.rect.y / self.width
            new_y = width * ratio_y
            sprite.init_rect(self.lines, width, new_y)

        radius = int(width / self.lines * self.TARGET_FACTOR)
        target_y = height - (height * self.TARGET_Y_FACTOR)
        for sprite in self.target_sprites.sprites():
            sprite.set_radius_and_y(radius, target_y)
            sprite.reload()
        return screen

    def run(self):
        is_running = True
        pause_flag = False
        last_target = None

        self.note_sprites = pygame.sprite.Group()
        self.target_sprites = self.init_targets()
        clock = pygame.time.Clock()

        frame_rate = 200
        while is_running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        self.on_end.emit()
                if event.type == NOTE_INCOMING:
                    try:
                        line = event.dict["line"]
                        field = event.dict["field"]
                        note = Note(line, field, self.RECT_FACTOR)
                        note.init_rect(self.lines, self.width)
                        self.note_sprites.add(note)
                    except Exception as e:
                        print(e)
                # Used for hiding and showing:
                # https://stackoverflow.com/questions/34910086/pygame-how-do-i-resize-a-
                # surface-and-keep-all-objects-within-proportionate-to-t
                if event.type == PAUSE:
                    self.center_position(self.p_width, self.p_height)
                    screen = pygame.display.set_mode(
                        (self.p_width, self.p_height), pygame.NOFRAME)
                    screen.blit(pygame.transform.scale(
                        self.screen, (self.p_width, self.p_height)), (0, 0))
                    self.redraw(screen, self.p_width, self.p_height)
                    pygame.display.flip()
                    pause_flag = True
                if event.type == CONTINUE:
                    self.center_position(self.width, self.height)
                    screen = pygame.display.set_mode(
                        (self.width, self.height), pygame.NOFRAME)
                    screen.blit(pygame.transform.scale(
                        self.screen, (self.width, self.height)), (0, 0))
                    self.screen = self.redraw(screen, self.width, self.height)
                    pygame.display.flip()
                    pause_flag = False
                if event.type == ACTION:
                    action_line = event.dict["line"]
                    target = self.get_target_by_id(action_line)
                    found_target = False
                    for note in self.note_sprites.sprites():
                        if note.field == 1 and note.line == action_line:
                            if note.has_hit(target):
                                self.on_hit.emit()
                                found_target = True
                                self.remove_rect(note)
                                self.note_sprites.remove(note)
                            else:
                                self.on_fail.emit()
                    if not found_target:
                        target.change_state(target.fail)
                        pygame.time.set_timer(CLEAR_TARGET, 100)
                    else:
                        found_target = False
                    last_target = target
                if event.type == CLEAR_MUSIC:
                    pygame.mixer.music.stop()
                if event.type == CLEAR_TARGET:
                    if last_target is not None:
                        last_target.change_state(last_target.inactive)
                if event.type == EXIT:
                    is_running = False
                if event.type == pygame.QUIT:
                    sys.exit()
            if not pause_flag:
                width, height = self.screen.get_size()
                self.screen.blit(self.background, (0, 0))
                for sprite in self.note_sprites.sprites():
                    self.remove_rect(sprite.rect)
                    if sprite.rect.top >= height - sprite.rect.height:
                        if sprite.field == 2:
                            sprite.move_to_field(1, self.lines, width)
                    if sprite.rect.y >= height:
                        self.on_fail.emit()
                        self.note_sprites.remove(sprite)
                        continue
                    self.screen.blit(self.background, sprite.rect, sprite.rect)
                self.note_sprites.update()
                self.note_sprites.draw(self.screen)
                self.target_sprites.draw(self.screen)
                pygame.display.flip()
                clock.tick(frame_rate)
        pygame.quit()

    def get_target_by_id(self, id):
        for target in self.target_sprites.sprites():
            if target.id == id:
                return target
        return None

    def remove_rect(self, rect):
        pygame.draw.rect(self.screen, (0, 0, 0), rect)


class Note(pygame.sprite.Sprite):

    def __init__(self, line, field, size_factor):
        super().__init__()
        self.line = line
        self.field = field

        self.size_factor = size_factor

    def reload(self):
        self.image, self.rect = self.__load_png__("sprites/note.png")

    def init_rect(self, lines, window_width, other_y=None):
        self.reload()
        line = self.line
        if self.field == 2:
            line += 8

        self.rect.x = self.calc_line_center(lines, window_width, line)
        if other_y is not None:
            self.rect.y = other_y
        else:
            self.rect.y = 0
        size = self.calc_size(lines, window_width)
        self.image = pygame.transform.scale(self.image, (size, size))

    def set_size(self, width, height):
        self.rect.width = width
        self.rect.height = height

    def update(self):
        self.rect = self.rect.move(0, 1)

    def move_to_field(self, field, lines, window_width):
        self.field = field
        size = self.calc_size(lines, window_width)
        center = self.calc_line_center(lines, window_width)
        self.rect.x = center - size / 2
        self.rect.y = 0

    def calc_size(self, lines, window_width):
        return int(window_width / lines * self.size_factor)

    def calc_line_center(self, lines, window_width, line=None):
        if line is None:
            line = self.line
        return (window_width / lines * line +
                window_width / lines * (line + 1)) / 2

    def has_hit(self, target):
        hit = False
        if self.rect.colliderect(target.rect):
            target.change_state(target.success)
            target.play()
            hit = True
        else:
            target.change_state(target.fail)
        pygame.time.set_timer(CLEAR_TARGET, 100)
        return hit

    # Pygame tutorial
    def __load_png__(self, name):
        # Load image and return image object
        fullname = name
        try:
            image = pygame.image.load(fullname)
            image = image.convert_alpha()
        except pygame.error as message:
            print('Cannot load image:', fullname)
            raise(SystemExit, message)
        return image, image.get_rect()


class Target(pygame.sprite.Sprite):

    def __init__(self, id, x, y, radius, images, sound):
        super().__init__()
        self.id = id
        self.inactive = images[0]
        self.fail = images[1]
        self.success = images[2]
        self.radius = radius
        self.pos = (x, y)
        self.current_state = self.inactive
        self.sound = sound
        self.change_state(self.current_state)

    def play(self):
        pygame.mixer.music.load(self.sound)
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.set_pos(1)
        pygame.mixer.music.play()
        pygame.time.set_timer(CLEAR_MUSIC, 1000)

    def set_radius_and_y(self, radius, y):
        self.radius = radius
        self.pos = (self.pos[0], y)

    def change_state(self, state):
        self.current_state = state
        self.reload()

    def reload(self):
        self.image, self.rect = self.__load_png__(self.current_state)
        self.image = pygame.transform.scale(
            self.image, (self.radius, self.radius))
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]

    def __load_png__(self, name):
        # Load image and return image object
        fullname = name
        try:
            image = pygame.image.load(fullname)
            if image.get_alpha is None:
                image = image.convert()
            else:
                image = image.convert_alpha()
        except pygame.error as message:
            print('Cannot load image:', fullname)
            raise(SystemExit, message)
        return image, image.get_rect()


class GameWidget(QtWidgets.QWidget):

    game_end = QtCore.pyqtSignal(int)

    def __init__(self, resolution, devices, score=0, game=None, parent=None):
        super(GameWidget, self).__init__(parent)
        self.res = resolution
        self.is_pause = False
        self.player = None
        self.conductor = None

        self.score = score

        self.game = game

        self.init_ui()
        self.init_devices(devices)
        self.init_game()

    def init_ui(self):
        width = self.res[0] * 0.6
        height = self.res[1] * 0.6
        self.setFixedSize(width, height)

        layout = QtWidgets.QVBoxLayout(self)
        font = QtGui.QFont("Times", 20, QtGui.QFont.Bold)
        self.points_player = QtWidgets.QLabel(
            "Points: " + str(self.score), parent=self)
        self.points_player.setFont(font)
        self.points_player.setStyleSheet('color: white')
        layout.addWidget(self.points_player, alignment=QtCore.Qt.AlignCenter)
        layout.setAlignment(QtCore.Qt.AlignTop)

        self.setLayout(layout)
        self.show()

    def init_devices(self, devices):
        if len(devices) > 0:
            self.player = devices[0]
            self.player.register_click_callback(
                lambda btn, is_down: self.on_button("player", btn, is_down))
            if len(devices) > 1:
                self.conductor = devices[1]
                self.conductor.register_click_callback(
                    lambda btn, is_down: self.on_button("conductor", btn, is_down))

    def init_game(self):
        if self.game is None:
            self.game = GameThread(self.res, parent=self)
        self.game.on_fail.connect(self.on_player_fail)
        self.game.on_hit.connect(self.on_player_success)
        self.game.on_end.connect(self.on_end)
        self.game.start()

        try:
            QtCore.QTimer.singleShot(
                500, lambda: self.on_button("conductor", 1, True))
        except Exception as e:
            print(traceback.format_exc())
        
    def on_end(self):
        print("end")
        self.game_end.emit(self.score)

    def update_score(self, name):
        if name == "player":
            self.player_score += 10
        else:
            self.player_score -= 10
        self.points_player.setText("Points: " + str(self.score))
        self.update()

    def on_player_fail(self):
        self.score -= 5
        self.points_player.setText("Points: " + str(self.score))
        self.update()

    def on_player_success(self):
        self.score += 5
        self.points_player.setText("Points: " + str(self.score))
        self.update()

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
