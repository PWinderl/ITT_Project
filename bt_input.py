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

    def __init__(self, bluetooth_address):
        print('BT Address: ', bluetooth_address)
        if bluetooth_address == "1":
            self.wm = wiimote.connect("b8:ae:6e:1b:5a:a6")
            #self.wm = wiimote.connect("b8:ae:6e:1b:ad:8c")
        else:
            self.wm = wiimote.connect("b8:ae:6e:ef:ef:d6")
        try:
            #
            pass
            #self.wm = wiimote.connect("b8:ae:6e:1b:ad:8c")
        except Exception as e:
            print(e)
            print("No valid bluetooth addresses.")
            sys.exit()
            return

        self.wm.buttons.register_callback(self.__on_press__)

        self.move_callback = None
        self.click_callback = None
        self.confirm_callback = None

        # activity recognizer
        ActivityRecognizer(self)

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
                        if self.click_callback is not None:
                            self.click_callback()
                    else:
                        self.wm.ir.unregister_callback(self.__on_move__)
                    if self.click_callback is not None:
                        self.click_callback()
                elif btn == 'A':
                    if self.confirm_callback is not None:
                        self.confirm_callback()
                elif btn == 'One':
                    if self.click_callback is not None:
                        self.click_callback(self.BTN_ONE, is_down)
                elif btn == 'Two':
                    if self.click_callback is not None:
                        self.click_callback(self.BTN_TWO, is_down)

    # TODO: somehow get widget resolution
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


"""
Code by Fabian - for merging purposes.

            if obj[0][0] == 'Left':
                print('Left')
                if self.click_callback is not None:
                    self.click_callback()
            if obj[0][0] == 'Up':
                print('Up')
                if self.click_callback is not None:
                    self.click_callback()
            if obj[0][0] == 'Right':
                print('Right')
                if self.click_callback is not None:
                    self.click_callback()
            if obj[0][0] == 'Down':
                print('Down')
                if self.click_callback is not None:
                    self.click_callback()
            if obj[0][0] == "One":
                print("One")
                if self.click_callback is not None:
                    # self.click_callback()
                    self.write_csv()
                    #self.activity_vals = []
                    #self.counter = 0
                    self.status = 1
            if obj[0][0] == "Two":
                print("Two")
                if self.click_callback is not None:
                    # self.click_callback()
                    self.status = 0
                    self.buffer()
                    # print(self.activity_vals)
                    # self.fft(activity_vals)
                    # print(self.activity_vals)
"""
