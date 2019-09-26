from transitions import *
import numpy as np
from time import *
from Adafruit_AMG88xx import *
import requests

class GridEye(object):

    def __init__(self, callback, event_handler):
        self.name = "GE"
        self.event = None
        self.callback = callback
        self.event_handler = event_handler
        self.sensor = Adafruit_AMG88xx()
        self.pixels = []
        # Initiating grid eye sensor
        # Setting 10 FPS
        self.sensor._fpsc.FPS = AMG88xx_FPS_10
        sleep(0.1)
        # print("Initialized Grid Eye")
        self.left_calibration = 0
        self.right_calibration = 0
        self.verbose = False
        self.status = "READING"
        self.prev_time = 0
        self.threshold_cross_count = 0
        self.server_root=None
        # self.ts["READING", "TRIGGERED", "COMPLETED"] = [-1, -1, -1]

        print("Initialized Grid Eye")

    def set_server_root(self,server_root):
        self.server_root=server_root

    def send_live_data(self,pixels):
        if self.server_root is None:
            return
        url = self.server_root + '/ge_live_viz/'+requests.utils.quote(str(pixels))
        response = requests.get(url)
        if response.status_code != 200:
            print("ge_live_data could not be sent! http response code: ",str(response.status_code))

    def set_status(self, status):
        self.status = status
        # self.ts[status] = time()
        self.event_handler(self)

    def get_status(self):
        return self.status

    def read_pixels(self):
        right_pixels = []
        left_pixels = []
        self.pixels = self.sensor.readPixels()
        # print("\nPixels: ", self.pixels)
        right_pixels = self.pixels[:32]
        left_pixels = self.pixels[32:]
        return left_pixels, right_pixels

    def set_threshold(self, pixels, threshold):
        current_threshold = int(np.mean(np.sort(pixels)[-5:]))
        if -2 < (current_threshold - threshold) > 2:
            if (int(time()) - self.prev_time) > 1:
                if self.verbose:
                    print("Crossed threshold : ", self.threshold_cross_count)
                self.prev_time = int(time())
                self.threshold_cross_count += 1
            else:
                self.threshold_cross_count = 0
        if self.threshold_cross_count > 5:
            if self.verbose:
              print("Prev Threshold : %d \t Current Threshold : %d"%(threshold, current_threshold))
            threshold =  current_threshold
            self.threshold_cross_count = 0
        return threshold

    def monitor_ones(self):
        self.read_pixels()
        threshold = int(np.mean(np.sort(self.pixels)[-5:]))
        first_direction = 0
        second_direction = 0
        self.set_status("READING")
        while True:

            if self.get_status() == "COMPLETED":
                sleep(0.1)
                continue

            self.read_pixels()
            threshold_updated = self.set_threshold(self.pixels, threshold)
            pixels_array = np.transpose(np.reshape(self.pixels, [8, 8]) > threshold_updated + 1).astype(int)
            right = pixels_array[:, 0:3]
            left = pixels_array[:, -3:]

            all_count = np.count_nonzero(pixels_array[:, 1:])
            right_count = np.count_nonzero(right)
            left_count = np.count_nonzero(left)

            self.send_live_data(pixels_array)
            if self.verbose:
                print("Grid Eye Output:")
                print(pixels_array)
                print("Right count: %d & Left count: %d\n" % (np.count_nonzero(right), np.count_nonzero(left)))
            # print("right:\n",pixels_array[:,0:3],"\nleft:\n",pixels_array[:,-3:],"\n")

            # print("All count", all_count)
            # print("Left count", left_count)
            # print("Right count", right_count)
            # print("")

            if all_count > 12:
                if first_direction == 0:
                    if left_count - right_count > 5 or left_count - right_count < -5:
                        first_direction = left_count - right_count
                        self.set_status("TRIGGERED")
                        # print("Set first_direction : ", first_direction)
                else:
                    second_direction = left_count - right_count
                    # print("Set second_direction", second_direction)
            else:
                if first_direction < 0 and second_direction < 0:
                    print("Bhag gaya :D")
                    self.event = -2
                    self.callback(self.event)
                    self.set_status("COMPLETED")
                elif first_direction < 0 and second_direction > 0:
                    print("Entry")
                    self.event = 1
                    self.callback(self.event)
                    self.set_status("COMPLETED")
                elif first_direction > 0 and second_direction < 0:
                    print("Exit")
                    self.event = -1
                    self.callback(self.event)
                    self.set_status("COMPLETED")
                elif first_direction > 0 and second_direction > 0:
                    print("Andar aa gaya :D")
                    self.event = 2
                    self.callback(self.event)
                    self.set_status("COMPLETED")
                else:
                    if self.get_status() == "TRIGGERED":
                        self.event=None
                        self.status="READING"
                        # self.event = None
                        # self.callback(self.event)  # Something wrong
                        # self.set_status("COMPLETED")
                        print("Something wrong:: first_direction: ", first_direction, ", second_direction:",
                              second_direction)
                first_direction = 0
                second_direction = 0

            sleep(0.05)

    def reset_status_and_data(self):
        self.event=None
        self.set_status("READING")

    def is_data_ok(self):
        if self.event is None or self.event == -2 or self.event == 2:
            return False
        else:
            return True

    def monitor(self):
        self.monitor_ones()
