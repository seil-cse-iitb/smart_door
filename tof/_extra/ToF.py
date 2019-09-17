#!/usr/bin/python

import sys, os
from statistics import median

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
# above code is for adding current folder as library path so that python search this directory also for any library

import time
import VL53L0X as VL


class ToF:

    def __init__(self, callback, event_handler):
        self.name = "ToF"
        self.height=None
        self.verbose = False
        self.tof = VL.VL53L0X()
        self.door_height = 2000
        self.session = False
        self.session_id = 0
        self.callback = callback
        self.event_handler = event_handler
        self.status = "READING"

    def set_status(self, status):
        self.status = status
        self.event_handler(self)

    def get_status(self):
        return self.status

    def monitor(self):
        self.tof.start_ranging(VL.VL53L0X_GOOD_ACCURACY_MODE)
        timing = self.tof.get_timing()
        if timing < 20000:
            timing = 20000

        reading_count = 0
        person_distance = 0
        distance_list = []
        self.set_status("READING")
        while True:

            if self.get_status() == "COMPLETED":
                time.sleep(0.1)
                continue

            distance = self.tof.get_distance()
            print(distance)
            if 0 < distance < 1600:
                if self.get_status() == "READING":
                    self.set_status("TRIGGERED")
                self.session = True
                self.session_id += 1
                if self.verbose:
                    print("%d mm, %d cm, %d" % (distance, (distance / 10), reading_count))
                person_distance += distance
                distance_list.append(distance)
                reading_count += 1
            else:
                if self.session:
                    self.height= min(distance_list)
                    if self.verbose:
                        print("Session completed: ", self.height)
                    self.callback(self.height)
                    self.set_status("COMPLETED")
                    # print("Session completed: ", (person_distance / reading_count))
                    self.session = False
                    distance_list = []
                    person_distance = 0
                    reading_count = 0
            time.sleep(timing / 1000000.00)

    def reset_status_and_data(self):
        self.height=None
        self.set_status("READING")

    def is_data_ok(self):
        if self.height is None:
            return False
        else:
            return True

    def test(self):
        # Create a bin object
        tof = VL.VL53L0X()

        # Start ranging
        tof.start_ranging(VL.VL53L0X_BETTER_ACCURACY_MODE)

        timing = tof.get_timing()
        if timing < 20000:
            timing = 20000
        print("Timing %d ms" % (timing / 1000))

        # for count in range(1, 101):
        count = 0
        while True:
            count += 1
            distance = tof.get_distance()
            if distance > 0:
                print("%d mm, %d cm, %d" % (distance, (distance / 10), count))
            time.sleep(timing / 1000000.00)

        tof.stop_ranging()
