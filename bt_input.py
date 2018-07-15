import wiimote
import sys
from transform import Transform
from pyqtgraph.Qt import QtGui, QtCore


# To connect to Wiimotes
class Device:

    def __init__(self, bluetooth_address):
        print('BT Address: ', bluetooth_address)
        if bluetooth_address == "1":
            self.wm = wiimote.connect("b8:ae:6e:1b:5a:a6")
        else:
            self.wm = wiimote.connect("b8:ae:6e:ef:ef:d6")

        try:
            #
            pass
            # self.wm = wiimote.connect("b8:ae:6e:1b:ad:8c")
        except Exception as e:
            print(e)
            print("No valid bluetooth addresses.")
            sys.exit()
            return

        # activity recognizer
        self.activity_recognizer()

        self.wm.buttons.register_callback(self.__on_press__)

        self.move_callback = None
        self.click_callback = None
        self.confirm_callback = None

    def register_move_callback(self, callback):
        self.move_callback = callback

    def register_click_callback(self, callback):
        self.click_callback = callback

    def register_confirm_callback(self, callback):
        self.confirm_callback = callback

    # Registers button pushes
    def __on_press__(self, objects):
        if objects is not None and len(objects) > 0:
            for btn_object in objects:
                btn = btn_object[0]
                is_down = btn_object[1]
                if btn == 'B':
                    if is_down:
                        self.wm.ir.register_callback(self.__on_move__)
                        if self.confirm_callback is not None:
                            self.confirm_callback()
                    else:
                        self.wm.ir.unregister_callback(self.__on_move__)
                    if self.click_callback is not None:
                        self.click_callback(2, is_down)
                elif btn == 'A':
                    if self.click_callback is not None:
                        self.click_callback(1, is_down)
                elif btn == 'One':
                    if self.click_callback is not None:
                        self.click_callback(3, is_down)
                elif btn == 'Two':
                    if self.click_callback is not None:
                        self.click_callback(4, is_down)

    def __on_move__(self, data):
        # Only accepts data that has all 4 leds
        if len(data) == 4:
            points = []
            for item in data:
                points.append((item['x'], item['y']))
            # P is the center point of the wiimote IR camera
            # DEST is the destination resolution
            # needs to have widget resolution!
            P, DEST = (1024 / 2, 768 / 2), (500, 500)
            try:
                x, y = Transform().transform(points, DEST, P)
            except Exception as e:
                print(e)
                x = y = -1
            if self.move_callback is not None:
                self.move_callback(x, y)

    def activity_recognizer(self):
        self._acc_vals = []
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update_all_sensors)
        self.set_update_rate()

    def update_all_sensors(self):
        if self.wm is None:
            return
        self._acc_vals = self.wm.accelerometer
        val = self._acc_vals
        # if 400 <= val[0] <= 450 and 425 <= val[1] <= 475 and 500 <= val[2] <= 545:
        #    print("Geige")
        # else:
        #    print("keine Geige")
        # print(self._acc_vals)

    def set_update_rate(self):
        self.wm.accelerometer.register_callback(self.update_accel)
        self.update_timer.start(1000.0 / 20)

    def update_accel(self, acc_vals):
        self._acc_vals = self.wm.accelerometer
