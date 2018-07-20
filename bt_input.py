#!/usr/bin/env python3
# coding: utf-8

"""
The module Bluetooth Innput takes care of the connection
between the wiimote.py of Raphael Wimmer (https://github.com/RaphaelWimmer/wiimote.py)
and the game.

Author: Thomas Oswald
"""

import wiimote
import sys
from transform import Transform
from activity_recognizer import ActivityRecognizer
from bluetooth import BluetoothError


class Device:

    """
    A Device is the representation of a Wiimote. As this is a multiplayer game,
    two devices will be connected to the game.
    """

    # Button codes
    BTN_A = 1
    BTN_B = 2
    BTN_ONE = 3
    BTN_TWO = 4

    # Moving average length
    MV_SIZE = 10

    # At the initialization wiimote.py tries to connect to a hardware address.
    def __init__(self, address):
        try:
            # This is for the lazy ones.
            if address == "1":
                self.wm = wiimote.connect("b8:ae:6e:1b:5a:a6")
                # self.wm = wiimote.connect("b8:ae:6e:1b:ad:8c")
            elif address == "2":
                self.wm = wiimote.connect("b8:ae:6e:ef:ef:d6")
            else:
                self.wm = wiimote.connect(address)
        except BluetoothError as e:
            print("BluetoothError: " + str(e))
            raise ValueError("No valid bluetooth address.")

        self.wm.buttons.register_callback(self.__on_press__)

        self.move_callback = None
        self.click_callback = None
        self.gesture_btn_callback = None
        self.confirm_callback = None
        self.current_w_size = (500, 500)
        self.points_arr = []

        # Instantiate the activity recognizer.
        self.ar = ActivityRecognizer(self)

    # If it is necessary for the projective transformation, the destination widget size can be changed.
    def set_widget_size(self, size):
        self.current_w_size = size

    # Registers a callback for the pointing functionality.
    # Everytime the Wiimote moves, this will print out the projected point on the destination widget.
    def register_move_callback(self, callback):
        self.move_callback = callback

    # Registers a callback for the button input.
    def register_click_callback(self, callback):
        self.click_callback = callback

    # Registers a callback for the player.
    # This is needed, because he needs to do a gesture before he is able to press a button.
    def register_gesture_btn_callback(self, callback):
        self.gesture_btn_callback = callback

    # Registers a callback that does not have the same parameters as the click callback.
    # The difference is, that the confirmation will only trigger, when a button is pressed down
    # and not when it is released.
    def register_confirm_callback(self, callback):
        self.confirm_callback = callback

    # on_press handles all button presses of a Wiimote and acts in a defined way.
    def __on_press__(self, objects):
        if objects is not None and len(objects) > 0:
            for btn_object in objects:
                btn = btn_object[0]
                is_down = btn_object[1]
                found_btn = None
                # Button push for signature confirm and "B-Note" playing
                if btn == 'B':
                    found_btn = self.BTN_B
                    if self.confirm_callback is not None and is_down:
                        self.confirm_callback()
                # Button hold for drawing gestures and signature
                elif btn == 'A':
                    if is_down and self.move_callback is not None:
                        self.points_arr = []
                        self.wm.ir.register_callback(self.__on_move__)
                    else:
                        self.wm.ir.unregister_callback(self.__on_move__)
                    found_btn = self.BTN_A
                # Button push for "One-Note" playing
                elif btn == 'One':
                    found_btn = self.BTN_ONE
                # Button push for "Two-Note" playing
                elif btn == 'Two':
                    found_btn = self.BTN_TWO

                if found_btn is not None:
                    if self.gesture_btn_callback is not None and self.ar.is_violin():
                        self.gesture_btn_callback(found_btn, is_down)

                    if self.click_callback is not None:
                        self.click_callback(found_btn, is_down)

    # This method executes a projective transformation,
    # when all 4 infrared light diodes are in the focus of the ir camera.
    def __on_move__(self, data):
        # Only accepts data that has all 4 leds
        if len(data) == 4:
            points = []
            for item in data:
                points.append((item['x'], item['y']))
            self.points_arr.append(points)
            if len(self.points_arr) == self.MV_SIZE:
                x, y = self.__project_points__(self.points_arr)
                if self.move_callback is not None:
                    self.move_callback(x, y)
                self.points_arr = []

    # This function projects a point from the source projection
    # to the destination projection and returns the coordinate.
    def __project_points__(self, array):

        points = self.__mv_calc__(array)

        # P is the center point of the wiimote IR camera
        # DEST is the destination resolution
        P, DEST = (1024 / 2, 768 / 2), self.current_w_size
        try:
            x, y = Transform().transform(points, DEST, P)
            return (x, y)
        except Exception as e:
            x = y = -1
            return (x, y)

    # This method calculates the mean over moving values.
    def __mv_calc__(self, values):
        result = []
        for idx in range(3):
            x_arr = []
            y_arr = []
            for points in values:
                point = points[idx]
                x_arr.append(point[0])
                y_arr.append(point[1])

            x = sum(x_arr) / len(x_arr)
            y = sum(y_arr) / len(y_arr)
            result.append((x, y))
        return result
