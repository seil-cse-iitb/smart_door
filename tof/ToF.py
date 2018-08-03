#!/usr/bin/python

import time
import VL53L0X


class ToF:

    def __init__(self):
        self.tof = VL53L0X.VL53L0X()
        self.door_height = 2000
        self.session = False
        self.session_id = 0

    def monitor(self):
        self.tof.start_ranging(VL53L0X.VL53L0X_GOOD_ACCURACY_MODE)
        timing = self.tof.get_timing()
        if timing < 20000:
            timing = 20000

        reading_count = 0
        person_distance = 0
        while True:
            distance = self.tof.get_distance()
            print(distance)
            if 0 < distance < 6000:
                self.session = True
                self.session_id += 1
                csv = open("tof_data.csv", "a+")
                record = str(self.session_id) + "," + str(distance) + "," + str(reading_count) + "\n"
                csv.write(record)
                print("%d mm, %d cm, %d" % (distance, (distance / 10), reading_count))
                person_distance += distance
                reading_count += 1
            else:
                if self.session:
                    self.session = False
                    print("Session completed: ", (person_distance / reading_count))
                    person_distance = 0
                    reading_count = 0
                    csv.close()
            time.sleep(timing / 1000000.00)

    # def calibrate(self):
    #     print("Calibrating ToF!")
    #
    #     self.tof.start_ranging(VL53L0X.VL53L0X_LONG_RANGE_MODE)
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
        tof = VL53L0X.VL53L0X()

        # Start ranging
        tof.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

        timing = tof.get_timing()
        if (timing < 20000):
            timing = 20000
        print("Timing %d ms" % (timing / 1000))

        for count in range(1, 101):
            distance = tof.get_distance()
            if (distance > 0):
                print("%d mm, %d cm, %d" % (distance, (distance / 10), count))
            time.sleep(timing / 1000000.00)

        tof.stop_ranging()
