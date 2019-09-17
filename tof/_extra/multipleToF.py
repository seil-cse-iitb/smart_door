#!/usr/bin/python

import sys, os
from statistics import median

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
# above code is for adding current folder as library path so that python search this directory also for any library

import time
import VL53L0X as VL
import RPi.GPIO as GPIO
import csv 

class ToF:

    def __init__(self,callback,event_handler):
        
        self.xshut1 = 4
        self.xshut2 = 17

        GPIO.setwarnings(False)

        # Setup GPIO for each XSHUT pin of the sensor
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.xshut1, GPIO.OUT)
        GPIO.setup(self.xshut2, GPIO.OUT)

        # Make all the XSHUT pins zero
        GPIO.output(self.xshut1, GPIO.LOW)
        GPIO.output(self.xshut2, GPIO.LOW)
        time.sleep(0.5)

        self.verbose = False
        self.tof1 = VL.VL53L0X(address=0x2B)
        self.tof2 = VL.VL53L0X(address=0x2D)
        GPIO.output(self.xshut1, GPIO.HIGH)
        time.sleep(0.5)
        self.tof1.start_ranging(VL.VL53L0X_BETTER_ACCURACY_MODE)
        
        GPIO.output(self.xshut2, GPIO.HIGH)
        time.sleep(0.5)
        self.tof2.start_ranging(VL.VL53L0X_BETTER_ACCURACY_MODE)

        # self.door_height = 2000
        # self.session = False
        # self.session_id = 0
        # self.callback = callback
        time.sleep(0.50)

    def monitor(self):
        
        timing = self.tof1.get_timing()
        if timing < 20000:
            timing = 20000

        reading_count = 0
        person_distance = 0
        distance_list1 = []
        distance_list2 = []
        session_count_list = []

        session_count = 1
        # session_data = { 
        #     "distance_list1" : [],
        #     "distance_list2" : [],
        #     "session_count" : []
        #     }

        while True:
            distance1 = self.tof1.get_distance()
            distance2 = self.tof2.get_distance()
            print("TOF1:",distance1,"TOF2:",distance2)
            # print(distance)
            # if 0 < distance1 < 650 or 0 < distance2 < 650:
            #     self.session = True
            #     self.session_id += 1
            #
            #     if self.verbose:
            #         print("\nTOF1: %d mm, %d cm, %d" % (distance1, (distance1 / 10), reading_count))
            #         print("TOF2: %d mm, %d cm, %d \n" % (distance2, (distance2 / 10), reading_count))
            #     person_distance += distance1
            #     # session_data["distance_list1"].append(distance1)
            #     # session_data["distance_list2"].append(distance2)
            #     # session_data["session_count"].append(session_count)
            #     distance_list1.append(distance1)
            #     distance_list2.append(distance2)
            #     session_count_list.append(session_count)
            #     reading_count += 1
            # else:
            #     if self.session:
            #         self.session = False
            #         session_count += 1
            #         # print("Session completed: ", (person_distance / reading_count))
            #         if self.verbose:
            #         #     print("Session completed for %d : %d" % (self.tof1.my_object_number, min(session_data["distance_list1"])))
            #         #     print("Session completed for %d : %d" % (self.tof2.my_object_number, min(session_data["distance_list2"])))
            #
            #             print("Session completed for %d : %d" % (self.tof1.my_object_number, min(distance_list1)))
            #             # print("Session completed for %d : %d" % (self.tof2.my_object_number, min(distance_list2)))
            #
            #         self.writeToCSV(session_count_list, distance_list1, distance_list2)
            #         self.callback(min(min(distance_list1), min(distance_list2)))
            #         # self.writeToCSV(session_data)
            #         # self.callback(min(min(session_data["distance_list1"]), min(session_data["distance_list2"])))
            #         # session_data = {
            #         #     "distance_list1" : [],
            #         #     "distance_list2" : [],
            #         #     "session_count" : []
            #         # }
            #         distance_list1 = []
            #         # distance_list2 = []
            #         session_count_list = []
            #
            #         reading_count = 0
            time.sleep(timing / 1000000.00)
    
    def writeToCSV(self, session_count_list, distance_list1, distance_list2):

        with open('heightData.csv', 'a') as datafile:
            writer = csv.writer(datafile, delimiter= ',')

            write_list = []
            for i in range(0, len(distance_list1)):
                write_list = [str(session_count_list[i]), str(distance_list1[i]), str(distance_list2[i])]
                writer.writerow(write_list)
        

    # def writeToCSV(self, session_data):
        # print(session_data)
        # with open('heightData.csv', 'a') as data:
            # fieldnames = ['Session ID', 'Sensor 1 Data', 'Sensor 2 Data']
            # writer = csv.DictWriter(data) # fieldnames=fieldnames)

            # writer.writeheader()
            # writer.writerow([session_data])

    # def calibrate(self):
    #     print("Calibrating tof1!")
    #
    #     self.tof1.start_ranging(VL.VL53L0X_LONG_RANGE_MODE)
    #
    #     timing = self.tof1.get_timing()
    #     if timing < 20000:
    #         timing = 20000
    #
    #     reading_count = 0
    #     for count in range(0, 100):
    #         distance = self.tof1.get_distance()
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
        # Start ranging
        timing_1 = self.tof1.get_timing()
        timing_2 = self.tof2.get_timing()

        if timing_1 < 20000:
            timing_1 = 20000
        print("Timing %d ms" % (timing_1 / 1000))

#        for count in range(1, 101):
        count = 0
        while(True):
            count += 1
            distance_1 = self.tof1.get_distance()
            distance_2 = self.tof2.get_distance()

            if (distance_1 > 0):
                print("Sensor 1 : %d mm, %d cm, %d" % (distance_1, (distance_1 / 10), count), " Sensor 2: %d mm, %d cm, %d" % (distance_2, (distance_2 / 10), count))
                # print("%d mm, %d cm, %d" % (distance_2, (distance_2 / 10), count))
            time.sleep(timing_1 / 1000000.00)

        self.tof1.stop_ranging()
        self.tof2.stop_ranging()

