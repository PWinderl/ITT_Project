import csv
import numpy as np
from sklearn import svm
from transform import Transform
from pyqtgraph.Qt import QtGui, QtCore
from numpy import sin, linspace, pi
from scipy import fft, arange

class ActivityRecognizer():

    def __init__(self, device):
        self.wm = device.wm
        self.device = device
        self.activity_recognizer()
        self.device.register_click_callback(self.on_click)

    # TODO: Fabian comment
    def is_violin(self):
        if self.check_activity()[0] == 0:
            return True
        return False

    # TODO: Fabian comment
    def check_activity(self):
        self.status = 1
        self.buffer()
        self.write_csv()
        self.status = 0
        return self.getActivity()
    
    def on_click(self, btn, is_down):
        if is_down:
            if btn == self.device.BTN_ONE:
                self.write_csv()
            if btn == self.device.BTN_TWO:
                self.status = 0

    def write_csv(self):
        # Writing csv file.
        with open("act.csv", "w", newline="") as f:
            writer = csv.writer(f)

    def refresh_csv(self):
        # Refreshing csv file, deleting old values.
        if self.counter == 10:
            with open("act.csv", "r") as f:
                reader = csv.reader(f)
                backup = list(reader)
                len_backup = len(backup)
                diff = int(len_backup / 2)
            with open("act.csv", "w", newline="") as f:
                writer = csv.writer(f)
                for x in range(diff, len_backup):
                    writer.writerow([backup[x][0], backup[x][1], backup[x][2]])
                self.counter = 0
        self.counter += 1

    def add_csv(self, vals):
        # Adding accelerometer values to csv file.
        with open("act.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([vals[0], vals[1], vals[2]])

    def read_csv(self, filename):
        # Reading CSV Files.
        with open(filename, "r") as f:
            reader = csv.reader(f)
            activity_vals = list(reader)
            return activity_vals

    def buffer_act(self):
        # This function reads in the current activity values and compares them with the trained SVM.
        act = self.read_csv("act.csv")
        act_vals = [act]
        act = self.avg(act_vals)
        act = [l[-self.min_len:] for l in act]
        act_freq = self.fft(act)
        self.current_activity = self.c.predict([act_freq[0]])
        return self.current_activity

    def buffer(self):
        # Preparing samples for SVM.
        # Reading in violin samples.
        vio_one = self.read_csv("vio.csv")
        vio_two = self.read_csv("vio2.csv")
        vio_three = self.read_csv("vio3.csv")
        vio_four = self.read_csv("vio4.csv")
        vio_vals = [vio_one, vio_two, vio_three, vio_four]
        # Reading in guitar samples.
        guitar_one = self.read_csv("guitar.csv")
        guitar_two = self.read_csv("guitar2.csv")
        guitar_three = self.read_csv("guitar3.csv")
        guitar_four = self.read_csv("guitar4.csv")
        guitar_vals = [guitar_one, guitar_two, guitar_three, guitar_four]
        # Reading in drums samples.
        drums_one = self.read_csv("drums.csv")
        drums_two = self.read_csv("drums2.csv")
        drums_three = self.read_csv("drums3.csv")
        drums_four = self.read_csv("drums4.csv")
        drums_vals = [drums_one, drums_two, drums_three, drums_four]
        # Calculating average for all samples.
        vio = self.avg(vio_vals)
        guitar = self.avg(guitar_vals)
        drums = self.avg(drums_vals)
        # Cutting off all samples to the same length.
        vio, guitar, drums = self.cut_off(vio, guitar, drums)
        # FFT Filter.
        vio_freq = self.fft(vio)
        guitar_freq = self.fft(guitar)
        drums_freq = self.fft(drums)
        # SVM.
        self.svm(vio_freq, guitar_freq, drums_freq)

    def avg(self, data):
        # This function calculates average values for a sample.
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
        return buffered_vals

    def cut_off(self, vio, guitar, drums):
        # This function cuts off samples to the same length.
        all_vals = vio + guitar + drums
        self.min_len = min([len(x) for x in all_vals])
        vio = [l[:self.min_len] for l in vio]
        guitar = [l[:self.min_len] for l in guitar]
        drums = [l[:self.min_len] for l in drums]
        return vio, guitar, drums

    def activity_recognizer(self):
        # This function initializes the activity recognizer.
        self.c = svm.SVC(gamma=0.001, C = 100, degree = 3)
        self.counter = 0
        self.min_len = 0
        self.write_csv()
        self.status = 0
        self.acc_vals = []
        # Preparing all samples for SVM.
        self.buffer()
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update_all_sensors)
        self.set_update_rate()

    def update_all_sensors(self):
        # Sensor Update.
        if self.wm is None:
            return

    def set_update_rate(self):
        # Update timer for accelerometer output.
        self.wm.accelerometer.register_callback(self.update_accel)
        self.update_timer.start(1000.0 / 20)

    def update_accel(self, acc_vals):
        # Update accelerometer values.
        self.acc_vals = self.wm.accelerometer
        if self.status == 0:
            self.add_csv(self.acc_vals)


    def fft(self, data):
        # Fast Fourier Transformation.
        data_freq = []
        for l in data:
            n = len(l)
            frq = np.abs(fft(l)/n)[1:n//2]
            data_freq.append(frq)
        return data_freq

    def svm(self, vio_freq, guitar_freq, drums_freq):
        # Support Vector Machine.
        vio = 0
        guitar = 1
        drums = 2
        categories = [vio] *3  + [guitar] * 3 + [drums] *3
        training_data = vio_freq[1:] + guitar_freq[1:] + drums_freq[1:]
        self.c.fit(training_data, categories)
