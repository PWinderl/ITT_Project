#!/usr/bin/env python3
# coding: utf-8

"""
By Thomas Oswald
"""

import wiimote
import sys
from transform import Transform
from activity_recognizer import ActivityRecognizer


# To connect to Wiimotes
class Device:

    BTN_A = 1
    BTN_B = 2
    BTN_ONE = 3
    BTN_TWO = 4

    def __init__(self, address):
        try:
            if address == "1":
                self.wm = wiimote.connect("b8:ae:6e:1b:5a:a6")
                # self.wm = wiimote.connect("b8:ae:6e:1b:ad:8c")
            elif address == "2":
                self.wm = wiimote.connect("b8:ae:6e:ef:ef:d6")
            else:
                self.wm = wiimote.connect(address)
        except Exception as e:
            print(e)
            print("No valid bluetooth addresses.")
            sys.exit()
            return

        self.wm.buttons.register_callback(self.__on_press__)

        self.move_callback = None
        self.click_callback = None
        self.gesture_btn_callback = None
        self.confirm_callback = None
        self.current_w_size = (500, 500)
        # activity recognizer
        self.ar = ActivityRecognizer(self)

    def set_widget_size(self, size):
        self.current_w_size = size

    def register_move_callback(self, callback):
        self.move_callback = callback

    def register_click_callback(self, callback):
        self.click_callback = callback

    def register_gesture_btn_callback(self, callback):
        self.gesture_btn_callback = callback

    def register_confirm_callback(self, callback):
        self.confirm_callback = callback

    def is_violin(self):
        if self.check_activity()[0] == 0:
            return True
        return False

    # Registers button pushes
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
                    if is_down:
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
                    if self.gesture_btn_callback is not None and self.is_violin():
                        self.gesture_btn_callback(found_btn, is_down)

                    if self.click_callback is not None:
                        self.click_callback(found_btn, is_down)

    def __on_move__(self, data):
        # Only accepts data that has all 4 leds
        if len(data) == 4:
            points = []
            for item in data:
                points.append((item['x'], item['y']))
            # P is the center point of the wiimote IR camera
            # DEST is the destination resolution
            # needs to have widget resolution!
            P, DEST = (1024 / 2, 768 / 2), self.current_w_size
            try:
                x, y = Transform().transform(points, DEST, P)
            except Exception as e:
                x = y = -1
            if self.move_callback is not None:
                self.move_callback(x, y)

    def check_activity(self):
        self.ar.status = 1
        self.ar.buffer()
        self.ar.write_csv()
        self.ar.status = 0
        return self.ar.getActivity()
