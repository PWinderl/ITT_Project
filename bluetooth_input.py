import wiimote
import sys
import csv
import numpy as np
from sklearn import svm
from transform import Transform
from pyqtgraph.Qt import QtGui, QtCore
from numpy import sin, linspace, pi
from scipy import fft, arange


# To connect to Wiimotes
class SetupBluetooth:
    def __init__(self, bluetooth_adress):
        print('BT Adress: ', bluetooth_adress)
        if bluetooth_adress == 1:
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
    def __on_press__(self, obj):
        if obj is not None and len(obj) > 0:
            if obj[0][0] == 'B':
                print('B-Button')
                # self.activity_recognizer()
                if obj[0][1] is True:
                    self.wm.ir.register_callback(self.__on_move__)
                    if self.click_callback is not None:
                        self.click_callback()
                else:
                    self.wm.ir.unregister_callback(self.__on_move__)
                    if self.click_callback is not None:
                        self.click_callback()
            if obj[0][0] == 'A':
                print('A-Button')
                if self.confirm_callback is not None:
                    self.confirm_callback()

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
                    #self.click_callback()
                    self.write_csv()
                    #self.activity_vals = []
                    #self.counter = 0
                    self.status = 1
            if obj[0][0] == "Two":
                print("Two")
                if self.click_callback is not None:
                    #self.click_callback()
                    self.status = 0
                    self.buffer()                        
                    #print(self.activity_vals)
                    #self.fft(activity_vals)
                    #print(self.activity_vals)

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

    def write_csv(self):
        with open("act.csv", "w", newline="") as f:
            writer = csv.writer(f)
            #writer.writerow(["x", "y", "z"])

    def add_csv(self, vals):
        #print("add")
        with open("act.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([vals[0], vals[1], vals[2]])

    def read_csv(self, filename):
        with open(filename, "r") as f:
            reader = csv.reader(f)
            activity_vals = list(reader)
            return activity_vals

    def buffer(self):
        act = self.read_csv("act.csv")
        act_vals = [act]
        #print(act_vals)
        vio_one = self.read_csv("vio.csv")
        vio_two = self.read_csv("vio2.csv")
        vio_three = self.read_csv("vio3.csv")
        vio_four = self.read_csv("vio4.csv")
        vio_vals = [vio_one, vio_two, vio_three, vio_four]
        #print(vio_vals)
        guitar_one = self.read_csv("guitar.csv")
        guitar_two = self.read_csv("guitar2.csv")
        guitar_three = self.read_csv("guitar3.csv")
        guitar_four = self.read_csv("guitar4.csv")
        guitar_vals = [guitar_one, guitar_two, guitar_three, guitar_four]
        drums_one = self.read_csv("drums.csv")
        drums_two = self.read_csv("drums2.csv")
        drums_three = self.read_csv("drums3.csv")
        drums_four = self.read_csv("drums4.csv")
        drums_vals = [drums_one, drums_two, drums_three, drums_four]
        act = self.avg(act_vals)
        #print(act)
        vio = self.avg(vio_vals)
        #print(vio)
        guitar = self.avg(guitar_vals)
        drums = self.avg(drums_vals)
        act, vio, guitar, drums = self.cut_off(act, vio, guitar, drums)
        act_freq = self.fft(act)
        #print(act_freq)
        vio_freq = self.fft(vio)
        #print(vio_freq)
        guitar_freq = self.fft(guitar)
        drums_freq = self.fft(drums)
        self.svm(act_freq, vio_freq, guitar_freq, drums_freq)

    def avg(self, data):
        buffered_vals = []
        for f in data:
            x = []
            y = []
            z = []
            avg = []
            for line in f:
                _x = int(line[0])
                _y = int(line[1])
                _z = int(line[2])
                x.append(_x)
                y.append(_y)
                z.append(_z)
                avg.append((_x + _y +_z) / 3)
            buffered_vals.append(avg)
        #print(buffered_vals)
        #vals = self.cut_off(buffered_vals)
        return buffered_vals

    def cut_off(self, act, vio, guitar, drums):
        all_vals = act + vio + guitar + drums
        #print(all_vals)
        min_len = min([len(x) for x in all_vals])
        print("len")
        print(min_len)
        act = [l[:min_len] for l in act]
        vio = [l[:min_len] for l in vio]
        guitar = [l[:min_len] for l in guitar]
        drums = [l[:min_len] for l in drums]
        #vals_two = [l[:min_len] for l in vals_two]
        #vals_three = [l[:min_len] for l in vals_three]
        #vals_four = [l[:min_len] for l in vals_four]
        #self.fft(vals)
        return act, vio, guitar, drums


    def activity_recognizer(self):
        self.status = 0
        self.counter = 0
        self.acc_vals = []
        #self.activity_vals = []
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update_all_sensors)
        self.set_update_rate()

    def update_all_sensors(self):
        if self.wm is None:
            return
        self.acc_vals = self.wm.accelerometer
        if self.status == 1:
            self.add_csv(self.acc_vals)
        #if self.status == 1:
        #    print(self.acc_vals)
        #    self.activity_vals.append(self.acc_vals)
        #if 400 <= val[0] <= 450 and 425 <= val[1] <= 475 and 500 <= val[2] <= 545:
        #    print("Geige")
        #else:
        #    print("keine Geige")
        #print(self.acc_vals)

    def set_update_rate(self):
        self.wm.accelerometer.register_callback(self.update_accel)
        self.update_timer.start(1000.0 / 20)

    def update_accel(self, acc_vals):
        self.acc_vals = self.wm.accelerometer

    def fft(self, data):
        print(data)
        data_freq = []
        for l in data:
            #print("l")
            #print(l)
            n = len(l)
            frq = np.abs(fft(l)/n)[1:n//2]
            data_freq.append(frq)
        #self.scv(vio_freq)
        return data_freq

    def svm(self, act_freq, vio_freq, guitar_freq, drums_freq):
        #print(act_freq)
        c = svm.SVC(gamma=0.001, C = 100, degree = 3)
        #print(c)
        vio = 0
        guitar = 1
        drums = 2
        categories = [vio] *3  + [guitar] * 3 + [drums] *3#+ [walk]*3
        print("WG")
        #print(categories)
        training_data = vio_freq[1:] + guitar_freq[1:] + drums_freq[1:]
        #print(training_data)
        c.fit(training_data, categories)
        result = c.predict([act_freq[0]])
        print(result)
