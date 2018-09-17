#!/usr/bin/python

import sys, os
from statistics import median

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
# above code is for adding current folder as library path so that python search this directory also for any library

import time
import VL53L0X as VL


class ToF:

    def __init__(self,callback):
        self.verbose = False
        self.tof = VL.VL53L0X()
        self.door_height = 2000
        self.session = False
        self.session_id = 0
        self.callback = callback

    def monitor(self):
        self.tof.start_ranging(VL.VL53L0X_GOOD_ACCURACY_MODE)
        timing = self.tof.get_timing()
        if timing < 20000:
            timing = 20000

        reading_count = 0
        person_distance = 0
        distance_list = []
        while True:
            distance = self.tof.get_distance()
        #    print(distance)
            if 0 < distance < 600:
                self.session = True
                self.session_id += 1
                if self.verbose:
                    print("%d mm, %d cm, %d" % (distance, (distance / 10), reading_count))
                person_distance += distance
                distance_list.append(distance)
                reading_count += 1
            else:
                if self.session:
                    self.session = False
                    # print("Session completed: ", (person_distance / reading_count))
                    if self.verbose:
                        print("Session completed: ", min(distance_list))
                    self.callback(min(distance_list))
                    distance_list = []
                    person_distance = 0
                    reading_count = 0
            time.sleep(timing / 1000000.00)

    # def calibrate(self):
    #     print("Calibrating ToF!")
    #
    #     self.tof.start_ranging(VL.VL53L0X_LONG_RANGE_MODE)
    #
    #     timing = self.tof.get_timing()
    #     if timing < 20000:
    #         timing = 20000
    #
    #     reading_count = 0
    #     for count in range(0, 100):
    #         distance = self.tof.get_distance()
    #         if 0 < distance < 6000:
    #             print("%d mm, %d cm, %d" % (distance, (distance / 10), count))
    #             self.door_height += distance
    #             reading_count += 1
    #         time.sleep(timing / 1000000.00)
    #
    #     if reading_count == 0:
    #         return False
    #
    #     self.door_height = self.door_height / reading_count
    #     print("Door Height: ", self.door_height)
    #     return True

    def test(self):
        # Create a bin object
        tof = VL.VL53L0X()

        # Start ranging
        tof.start_ranging(VL.VL53L0X_BETTER_ACCURACY_MODE)

        timing = tof.get_timing()
        if (timing < 20000):
            timing = 20000
        print("Timing %d ms" % (timing / 1000))

##        for count in range(1, 101):
        count = 0
        while(True):
            count += 1
            distance = tof.get_distance()
            if (distance > 0):
                print("%d mm, %d cm, %d" % (distance, (distance / 10), count))
            time.sleep(timing / 1000000.00)

        tof.stop_ranging()
