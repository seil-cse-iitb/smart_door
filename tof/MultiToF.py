#!/usr/bin/python

import sys, os
import RPi.GPIO as GPIO
from statistics import median

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
# above code is for adding current folder as library path so that python search this directory also for any library

import time
import VL53L0X as VL


class ToF:

    def __init__(self, xshut_pins, addresses, is_multiple_tof, callback, event_handler):

        self.name = "ToF"
        self.height = None
        self.verbose = False
        self.tofs = []

        if is_multiple_tof:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)

            for pin_index in range(0, len(xshut_pins)):
                GPIO.setup(xshut_pins[pin_index], GPIO.OUT)
                time.sleep(0.1)
                GPIO.output(xshut_pins[pin_index], GPIO.LOW)
                time.sleep(0.1)

                self.tofs.append(VL.VL53L0X(address=addresses[pin_index]))
                GPIO.output(xshut_pins[pin_index], GPIO.HIGH)
                time.sleep(0.5)

                self.tofs[pin_index].start_ranging(VL.VL53L0X_GOOD_ACCURACY_MODE)

                time.sleep(0.5)

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
        timing = self.tofs[0].get_timing()
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
            distance = 99999
            for tof in self.tofs:
                distance =  min(distance, tof.get_distance())
            #    print(distance)
            if 0 < distance < 1000:
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

        timing = self.tofs[0].get_timing()
        if timing < 20000:
            timing = 20000
        reading_count = 0
        person_distance = 0
        distance_list = []

        while True:

            distance = 99999
            for tof in self.tofs:
                distance = min(distance, tof.get_distance())
            print(distance)
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
                    self.height = min(distance_list)
                    if self.verbose:
                        print("Session completed: ", self.height)
                    self.callback(self.height)
                    # print("Session completed: ", (person_distance / reading_count))
                    self.session = False
                    distance_list = []
                    person_distance = 0
                    reading_count = 0
            time.sleep(timing / 1000000.00)
