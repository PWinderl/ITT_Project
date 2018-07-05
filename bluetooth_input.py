# import wiimote
import sys
from transform import Transform


# To connect to Wiimotes
class SetupBluetooth:
    def __init__(self, bluetooth_adress):
        try:
            self.wm = wiimote.connect(bluetooth_adress)
        except BluetoothError:
            print("No valid bluetooth addresses.")
            sys.exit()
            return
        self.wm.buttons.register_callback(self.__on_press__)

        self.move_callback = None
        self.click_callback = None

    def register_move_callback(self, callback):
        self.move_callback = callback

    def register_click_callback(self, callback):
        self.click_callback = callback

    # Registers button pushes
    def __on_press__(self, obj):
        if obj is not None and len(obj) > 0:
            if obj[0][0] == 'B':
                if obj[0][1] is True:
                    self.wm.ir.register_callback(self.__on_move__)
                    if self.click_callback is not None:
                        self.click_callback()
                else:
                    self.wm.ir.unregister_callback(self.__on_move__)
                    if self.click_callback is not None:
                        self.click_callback()
            if obj[0][0] == 'Left':
                self.click_callback()
            if obj[0][0] == 'Up':
                self.click_callback()
            if obj[0][0] == 'Right':
                self.click_callback()
            if obj[0][0] == 'Down':
                self.click_callback()

    def __on_move__(self, data):
        # Only accepts data that has all 4 leds
        if len(data) == 4:
            points = []
            for item in data:
                points.append((item['x'], item['y']))
            # P is the center point of the wiimote IR camera
            # DEST is the destination resolution
            P, DEST = (1024 / 2, 768 / 2), (1920, 1080)
            try:
                x, y = Transform().transform(points, DEST, P)
            except Exception as e:
                print(e)
                x = y = -1
            if self.move_callback is not None:
                self.move_callback(x, y)