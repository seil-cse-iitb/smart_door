import sys, os

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
# above code is for adding current folder as library path so that python search this directory also for any library

import math
import time
# from sklearn import preprocessing, svm
# import pandas as pd
import numpy as np
import serial
from scipy import signal


class WeightMat:

    def __init__(self, serial_name, callback, event_handler):
        self.name = "WM"
        self.weight=None
        self.steps=None
        self.serial = None
        self.initialize_serial(serial_name)
        self.reading_started = False
        self.record_count = 1
        self.readings = []
        self.can_send = False
        self.verbose = False
        self.callback = callback
        self.event_handler = event_handler
        self.status = "READING"

    def read(self):
        line = str(self.serial.readline())[2:-5]
        # print(line)
        # line = str(self.s.readline())
        try:
            reading = 0.0
            if (len(line.strip()) > 0):
                reading = float(line.strip())
                # print(reading)
            else:
                print("blank value;\n")
            # print(reading)
        except Exception as e:
            print(line)
            print("Exception " + e)
            return -1
        return reading

    def initialize_serial(self, serial_name):
        try:
            self.serial = serial.Serial("/dev/" + serial_name, 115200, timeout=1)
            print("Calibrating....please don't put any weight on mat!")
            time.sleep(2)
            print("Weight mat on Duty!")
        except:
            print("Serial port is not connected: ", serial_name)
        skip = 20
        while skip > 0:
            self.serial.readline()
            skip -= 1

    def set_verbose(self, value):
        self.verbose = value

    def extract_features(self, readings):
        # global data
        if len(readings) < 2:
            return False
        readings_sorted_desc = readings
        peak_index = signal.find_peaks_cwt(readings, widths=np.array([5]))
        steps = len(peak_index)
        if steps > 2:
            steps = 2
        readings_sorted_desc.sort(reverse=True)
        difference_in_kg = 0
        if len(readings) >= 3:
            difference_in_kg = readings_sorted_desc[0] - readings_sorted_desc[1]
            difference_in_kg += readings_sorted_desc[1] - readings_sorted_desc[2]
            difference_in_kg = difference_in_kg / 1000
        readings_sorted_desc = np.array(readings_sorted_desc)
        limit = readings_sorted_desc[1] - 35000
        readings_sorted_desc = readings_sorted_desc[readings_sorted_desc >= limit]
        offset = 0
        if 15 < difference_in_kg <= 30:
            offset = 1
        elif difference_in_kg > 30:
            if len(readings_sorted_desc) > 5:
                offset = 2
            else:
                offset = 1
        if offset == 1:
            # percent = 20 * 10.2 / (len(readings_sorted_desc) - offset)
            if len(readings_sorted_desc) > 20:
                percent = 40
                offset = 2
            elif len(readings_sorted_desc) > 14:
                percent = 45
                offset = 1
            elif len(readings_sorted_desc) > 5:
                percent = 60
            else:
                percent = 50
        elif offset == 2:
            # percent = 30 * 10.2 / (len(readings_sorted_desc) - offset)
            percent = 40
        else:
            # percent = 35 * 10.2 / (len(readings_sorted_desc) - offset)
            if len(readings_sorted_desc) > 20:
                percent = 40
                offset = 2
            elif len(readings_sorted_desc) > 14:
                percent = 55
                offset = 1
            elif len(readings_sorted_desc) > 5:
                percent = 55
            else:
                percent = 80

        top_readings_with_offset = np.array(
            readings_sorted_desc[offset:offset + math.floor(percent * (len(readings_sorted_desc) - offset) / 100)])
        avg_weight_v1 = top_readings_with_offset.mean()
        # avg_weight_v2 = (readings[peak_index[0]] + readings[peak_index[0] + 1] + readings[peak_index[0] + 2]) / 3
        # print(readings_sorted_desc)
        if self.verbose:
            print("Difference in kg: ", difference_in_kg)
            print(top_readings_with_offset)
            print("No of readings: ", len(readings_sorted_desc))
            print("offset: ", offset)
            print("percent: ", percent)
            print("Avg Weight v1: ", avg_weight_v1)
            # print("Avg Weight v2: ", (2 * avg_weight_v1 + avg_weight_v2) / 3)
            # print(readings[peak_index[0]], " ", readings[peak_index[len(peak_index) - 1]])
            print("Steps: ", steps)
        # record = [['shaunak', math.floor(169 + random.rand() * 7),
        # round(math.floor(avg_weight_v1 / 100) / 10),
        # steps]]

        record = [[round(math.floor(avg_weight_v1 / 100) / 10), steps]]  # weight,steps
        # print(record)
        # data = data.append(pd.DataFrame(record,
        # columns=['name', 'height', 'weight_v1', 'steps']))
        # data.to_csv("_test.csv", index=False)

        return record

    def is_triggered(self):
        return self.reading_started

    def send(self, record):
        if self.verbose:
            print(record, " Send Function yet to write")
        self.callback(record[0][0], record[0][1])
        return record

    def set_status(self, status):
        self.status = status
        self.event_handler(self)

    def get_status(self):
        return self.status

    def is_data_ok(self):
        if self.weight is not None and self.steps is not None:
            return True
        else:
            return False

    def reset_status_and_data(self):
        self.weight=None
        self.steps=None
        self.set_status("READING")

    def monitor(self):
        self.set_status("READING")
        while True:
            if self.get_status() == "COMPLETED":
                time.sleep(0.1)
                continue

            reading = abs(self.read())
            #print(abs(reading))
            if reading > 20000:
                self.reading_started = True
                self.readings.append(reading)
                if self.get_status() == "READING":
                    self.set_status("TRIGGERED")
                #print(reading)
            elif self.reading_started:
                self.reading_started = False
                self.record_count += 1
                record = self.extract_features(self.readings)
                if record:
                    self.weight=record[0][0]
                    self.steps=record[0][1]
                    self.callback(self.weight, self.steps)
                    self.set_status("COMPLETED")
                else:
                    print("Very less readings! Check weightmat connections![Readings:" + str(self.readings) + "]")
                    self.callback(None, None)
                    self.set_status("COMPLETED")
                if self.verbose:
                    print(self.readings)
                self.readings.clear()
    
    def test(self):
        self.set_status("READING")
        while True:
            reading = abs(self.read())
            #print(abs(reading))
            if reading > 20000:
                self.reading_started = True
                self.readings.append(reading)
                if self.get_status() == "READING":
                    self.set_status("TRIGGERED")
                print(reading)
            elif self.reading_started:
                self.reading_started = False
                self.record_count += 1
                record = self.extract_features(self.readings)
                if record:
                    self.weight=record[0][0]
                    self.steps=record[0][1]
                    self.callback(self.weight, self.steps)
                    self.set_status("COMPLETED")
                else:
                    print("Very less readings! Check weightmat connections![Readings:" + str(self.readings) + "]")
                    self.callback(None, None)
                    self.set_status("COMPLETED")
                if self.verbose:
                    print(self.readings)
                self.readings.clear()
