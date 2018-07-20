#!/usr/bin/env python3
# coding: utf-8

"""
The Game module consists of three classes that are implementing the game itself.
GameWidget, on the other side, represents the container in which the game runs and
displays the points the player scored.

Author: Thomas Oswald
"""

from PyQt5 import QtWidgets, QtCore, Qt, QtGui
import sys
import pygame
import os
import time

# pygame event codes
NOTE_INCOMING = pygame.USEREVENT + 1
PAUSE = pygame.USEREVENT + 2
CONTINUE = pygame.USEREVENT + 3
ACTION = pygame.USEREVENT + 4
CLEAR_TARGET = pygame.USEREVENT + 5
EXIT = pygame.USEREVENT + 6
CLEAR_MUSIC = pygame.USEREVENT + 7

# The limit which defines, that the player
# will loose or win, when he reaches it.
# negative -> lost
# positive -> won
SCORE_LIMIT = 30
NOTE_LIMIT = 20

# The frame rate in which the game will run.
FRAME_RATE = 200

# Loads the image and returns an image object.
# Out of a pygame tutorial
# https://www.pygame.org/docs/tut/tom_games6.html


def __load_png__(name):
    fullname = name
    try:
        image = pygame.image.load(fullname)
        image = image.convert_alpha()
    except pygame.error as message:
        print('Cannot load image:', fullname)
        raise(SystemExit, message)
    return image, image.get_rect()


class GameThread(QtCore.QThread):

    """
    The GameThread is, like its name, a thread that executes the game.
    As pygame takes a whole thread to run (while loop) it needs to be done that way.
    Furthermore, this ensures that the game logic is separated from the rest.
    """

    # game signals
    on_hit = QtCore.pyqtSignal()
    on_fail = QtCore.pyqtSignal()
    on_end = QtCore.pyqtSignal()

    # color codes
    WHITE = (255, 255, 255)
    GREEN = (100, 250, 115)

    # size factors of
    # note and targets
    RECT_FACTOR = 0.2
    TARGET_FACTOR = 0.3
    TARGET_Y_FACTOR = 0.1

    # target state images
    TARGETS = [["sprites/a_inactive.png", "sprites/a_fail.png", "sprites/a_success.png"],
               ["sprites/b_inactive.png", "sprites/b_fail.png",
                   "sprites/b_success.png"],
               ["sprites/one_inactive.png", "sprites/one_fail.png",
                   "sprites/one_success.png"],
               ["sprites/two_inactive.png", "sprites/two_fail.png", "sprites/two_success.png"]]

    # sounds for each target.
    SOUNDS = ["sounds/violin_c.wav", "sounds/violin_f.wav",
              "sounds/violin_g.wav", "sounds/violin_a.wav"]

    def __init__(self, res, parent=None):
        super(GameThread, self).__init__(parent)
        self.res = res
        width, height = res
        self.width = int(width * 0.5)
        self.height = int(height * 0.5)
        self.center_position(self.width, self.height)

        # size of pause window
        self.p_width, self.p_height = (300, 300)

        # 8 lines and 4 for spacing between screens
        self.lines = 8 + 4

        # Init pygame
        pygame.init()

        # Define size of pygame
        self.screen = pygame.display.set_mode(
            (self.width, self.height), pygame.NOFRAME)
        self.circles = []
        self.rects = []
        self.background = self.init_background(self.screen)

    # This function centers the pygame window relative to the screen.
    def center_position(self, width, height):
        full_width, full_height = self.res
        frame_x = (full_width - width) / 2
        frame_y = (full_height - height) / 2
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (frame_x, frame_y)

    # This method creates the lines in which the note will move.
    # Furthermore it draws an green separator for the player view and the conductor view.
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

    # Adding targets to the game and positions them.
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

    # After switching the widgets, the game needs to be redrawn.
    # Depending whether the game will be shown or minimized,
    # the game will be scaled accordingly.
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

    # This is the game loop.
    # When the game is running it will first look into the event chain.
    # After that is done, the positioning and rendering will take place.
    def run(self):
        try:
            is_running = True
            pause_flag = False
            last_targets = []

            self.note_sprites = pygame.sprite.Group()
            self.target_sprites = self.init_targets()
            clock = pygame.time.Clock()

            while is_running:
                for event in pygame.event.get():
                    # Emergency exit event.
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pause_flag = True
                            pygame.event.post(pygame.event.Event(pygame.QUIT))
                            print("Taking the emergency exit.")
                    # When the conductor plays a note, this event will be fired.
                    # As such, a note will be created and added to the "to-be-rendered" sprites.
                    if event.type == NOTE_INCOMING:
                        if len(self.note_sprites.sprites()) < NOTE_LIMIT:
                            try:
                                line = event.dict["line"]
                                field = event.dict["field"]
                                note = Note(line, field, self.RECT_FACTOR)
                                note.init_rect(self.lines, self.width)
                                self.note_sprites.add(note)
                            except Exception as e:
                                print(e)
                                print("Note creating failed.")
                    # The behavior when the game will be paused.
                    # Used for scaling:
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

                    # Scaling the window back to its original state
                    # and drawing all content on it again.
                    if event.type == CONTINUE:
                        self.center_position(self.width, self.height)
                        screen = pygame.display.set_mode(
                            (self.width, self.height), pygame.NOFRAME)
                        screen.blit(pygame.transform.scale(
                            self.screen, (self.width, self.height)), (0, 0))
                        self.screen = self.redraw(
                            screen, self.width, self.height)
                        pygame.display.flip()
                        pause_flag = False

                    # This event is fired when the player is successfully
                    # executing the gesture and pressed a button.
                    # This code block will then examine whether it was the right one
                    # and if it is on point.
                    # According to the result the target state will be set and
                    # the score will be updated.
                    if event.type == ACTION:
                        action_line = event.dict["line"]
                        target = self.get_target_by_id(action_line)
                        found_target = False
                        if len(self.note_sprites.sprites()) == 0:
                            target.change_state(target.fail)
                            pygame.time.set_timer(CLEAR_TARGET, 100)
                            self.on_fail.emit()
                        else:
                            for note in self.note_sprites.sprites():
                                if note.field == 1 and note.line == action_line:
                                    if note.has_hit(target):
                                        target.change_state(target.success)
                                        self.on_hit.emit()
                                        pygame.time.set_timer(CLEAR_TARGET, 100)
                                        found_target = True
                                        self.remove_rect(note)
                                        self.note_sprites.remove(note)
                            if not found_target:
                                self.on_fail.emit()
                                target.change_state(target.fail)
                                pygame.time.set_timer(CLEAR_TARGET, 100)
                        last_targets.append(target)
                    if event.type == CLEAR_MUSIC:
                        pygame.mixer.music.stop()
                    if event.type == CLEAR_TARGET:
                        for target in last_targets:
                            target.change_state(target.inactive)
                        last_targets = []
                    if event.type == EXIT:
                        is_running = False
                    if event.type == pygame.QUIT:    
                        self.on_end.emit()
                        pygame.quit()
                        sys.exit()
                        return

                # This code block takes care of positioning and rendering.
                if not pause_flag:
                    width, height = self.screen.get_size()
                    self.screen.blit(self.background, (0, 0))
                    # Checking, whether the note is out of sight.
                    # If it is on the conducter side, it will be moved to the player.
                    # Therefore, if it is on the players side, the player will loose points.
                    for sprite in self.note_sprites.sprites():
                        self.remove_rect(sprite.rect)
                        if sprite.rect.top >= height - sprite.rect.height:
                            if sprite.field == 2:
                                sprite.move_to_field(1, self.lines, width)
                        elif sprite.rect.y > height and sprite.field == 1:
                            print("rect under height")
                            target = self.get_target_by_id(sprite.line)
                            self.on_fail.emit()
                            target.change_state(target.fail)
                            last_targets.append(target)
                            pygame.time.set_timer(CLEAR_TARGET, 100)
                            self.note_sprites.remove(sprite)
                            continue
                        self.screen.blit(
                            self.background, sprite.rect, sprite.rect)

                    # Rendering the game objects.
                    self.note_sprites.update()
                    self.note_sprites.draw(self.screen)
                    self.target_sprites.draw(self.screen)
                    pygame.display.flip()
                    clock.tick(FRAME_RATE)
        except Exception as e:
            print(e)

    def get_target_by_id(self, id):
        for target in self.target_sprites.sprites():
            if target.id == id:
                return target
        return None

    # Draws an game on top of the old note, so it won't leave a trace behind.
    def remove_rect(self, rect):
        pygame.draw.rect(self.screen, (0, 0, 0), rect)


class Note(pygame.sprite.Sprite):

    """
    A Note will be casted by the conducter. After that
    it moves along its line until it reaches the target.
    """

    def __init__(self, line, field, size_factor):
        super().__init__()
        self.line = line
        self.field = field
        self.image = None
        self.size_factor = size_factor

    def reload(self):
        if self.image is None:
            self.image, self.rect = __load_png__("sprites/note.png")

    # This method initializes the bounding rect, which scales and positions the object.
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

    # The update method moves the object.
    # This method will be executed every loop.
    def update(self):
        self.rect = self.rect.move(0, 1)

    # Moves the note to another field.
    # This means: changing to the players or conductors view.
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

    # Finds out whether the note collided with a target.
    def has_hit(self, target):
        hit = False
        if self.rect.colliderect(target.rect):
            target.play()
            target.change_state(target.success)
            hit = True
        else:
            target.change_state(target.fail)
        pygame.time.set_timer(CLEAR_TARGET, 100)
        return hit


class Target(pygame.sprite.Sprite):

    """
    A Target is the point that tells the player, when he has to push a button.
    Naturally, this should only be done, when a note is right on top of it.
    """

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

    # Plays the sound exactly one second.
    def play(self):
        pygame.mixer.music.load(self.sound)
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play()
        pygame.time.set_timer(CLEAR_MUSIC, 1000)

    def set_radius_and_y(self, radius, y):
        self.radius = radius
        self.pos = (self.pos[0], y)

    # The state defines, which image the target is displaying.
    # The different states: inactive, fail, success.
    def change_state(self, state):
        self.current_state = state
        self.reload()

    def reload(self):
        self.image, self.rect = __load_png__(self.current_state)
        self.image = pygame.transform.scale(
            self.image, (self.radius, self.radius))
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]


class GameWidget(QtWidgets.QWidget):

    """
    The GameWidget is the container and the border for the pygame window.
    It displays the score and the message after a minigame.
    """

    game_end = QtCore.pyqtSignal(int)

    def __init__(self, resolution, parent=None):
        super(GameWidget, self).__init__(parent)
        self.res = resolution
        self.is_pause = False
        self.player = None
        self.conductor = None
        self.score = 0
        self.timer = None
        self.init_ui()

    def start(self, devices, game=None, score=0):
        self.score = score
        self.show()
        self.setHidden(False)
        self.init_devices(devices)
        self.game = self.init_game(game)

    def hide(self):
        if self.player is not None:
            self.player.unregister_callbacks()
        if self.conductor is not None:
            self.conductor.unregister_callbacks()
        self.setHidden(True)
        self.close()

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
        self.setHidden(True)

    def init_devices(self, devices):
        if len(devices) > 0:
            self.player = devices[0]
            self.player.register_gesture_btn_callback(
                lambda btn, is_down: self.on_button("player", btn, is_down))
            if len(devices) > 1:
                self.conductor = devices[1]
                self.conductor.register_click_callback(
                    lambda btn, is_down: self.on_button("conductor", btn, is_down))

    # Starts a new Gamethread when it is not already running
    # and connects different slots to its signals.
    def init_game(self, game):
        if game is None:
            game = GameThread(self.res, parent=self)
        game.on_fail.connect(self.on_player_fail)
        game.on_hit.connect(self.on_player_success)
        game.on_end.connect(self.on_end)
        game.start()

        # This is important, because the game is running behind the minigame widget,
        # when the widgets change. So, the game needs to be brought to the front again.
        # Furthermore, it is an external command that was not installed by the standard
        # Debian installation. Read the instructions for further information.
        # Sets focus to pygame window.
        os.system("wmctrl -a pygame")
        return game

    # This method updates the score after the minigame ended.
    # Additionally, it displays the winner for a short time.
    def update_score(self, name):
        text = name + " won"
        if name == "player":
            self.score += 10
        else:
            self.score -= 10

        self.points_player.setText(text)
        self.update()

        def callback():
            self.points_player.setText("Points: " + str(self.score))
            self.update()
            self.check_score()

        self.start_timer(callback, 1000)

    def check_score(self):
        print(self.score)
        if abs(self.score) >= SCORE_LIMIT:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    # Starting a timer for a one time execution of an callback.
    # This was seen at
    # https://stackoverflow.com/questions/46656634/pyqt5-qtimer-count-until-specific-seconds
    def start_timer(self, callback, ms):
        def handler():
            callback()
            self.timer.stop()
            self.timer.deleteLater()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(handler)
        self.timer.start(ms)

    def on_player_fail(self):
        self.score -= 5
        self.points_player.setText("Points: " + str(self.score))
        self.update()
        self.check_score()

    def on_player_success(self):
        self.score += 5
        self.points_player.setText("Points: " + str(self.score))
        self.update()
        self.check_score()

    # Depending who pressed a button, different events will be fired.
    def on_button(self, char, btn, is_down):
        if not self.is_pause and is_down:
            if char == "player":
                print("button pressed char")
                pygame.event.post(pygame.event.Event(
                    ACTION, {"line": btn - 1}))
            elif char == "conductor":
                print("button pressed conductor")
                pygame.event.post(pygame.event.Event(
                    NOTE_INCOMING, {"line": btn - 1, "field": 2}))

    def on_pause(self):
        self.game.on_fail.disconnect(self.on_player_fail)
        self.game.on_hit.disconnect(self.on_player_success)
        self.game.on_end.disconnect(self.on_end)
        pygame.event.post(pygame.event.Event(PAUSE))
        self.is_pause = True

    def on_continue(self):
        pygame.event.post(pygame.event.Event(CONTINUE))
        self.is_pause = False

    def on_end(self):
        try:
            if self.timer is not None:
                self.timer.stop()
                self.timer.deleteLater()
        except RuntimeError as e:
            print("QTimer has already been deleted")
        self.game.on_fail.disconnect(self.on_player_fail)
        self.game.on_hit.disconnect(self.on_player_success)
        self.game.on_end.disconnect(self.on_end)
        self.game_end.emit(self.score)

    def closeEvent(self, event):
        return super().closeEvent(event)
