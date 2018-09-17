from transitions import *
import numpy as np
import random
import re
from time import *
from Adafruit_AMG88xx import *
import sys
import csv

class EntryExitDFA(object):
    states = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    triggers = ["OO", "OI", "IO", "II"]  # [0,1,2,3] #["00","01","10","11"]

    def __init__(self, callback):
        self.callback = callback
        # print("DFA init!")

        self.machine = Machine(model=self, states=EntryExitDFA.states, initial="0")

        self.machine.add_transition(trigger=self.triggers[0], source="0", dest="0")
        self.machine.add_transition(trigger=self.triggers[1], source="0", dest="1")
        self.machine.add_transition(trigger=self.triggers[2], source="0", dest="2")
        # self.machine.add_transition(trigger=self.triggers[3], source="0", dest=")"

        self.machine.add_transition(trigger=self.triggers[0], source="1", dest="0")
        self.machine.add_transition(trigger=self.triggers[1], source="1", dest="1")
        self.machine.add_transition(trigger=self.triggers[2], source="1", dest="3")
        self.machine.add_transition(trigger=self.triggers[3], source="1", dest="4")

        self.machine.add_transition(trigger=self.triggers[0], source="2", dest="0")
        self.machine.add_transition(trigger=self.triggers[1], source="2", dest="5")
        self.machine.add_transition(trigger=self.triggers[2], source="2", dest="2")
        self.machine.add_transition(trigger=self.triggers[3], source="2", dest="6")

        self.machine.add_transition(trigger=self.triggers[0], source="3", dest="7", after='exit')
        self.machine.add_transition(trigger=self.triggers[1], source="3", dest="1")
        self.machine.add_transition(trigger=self.triggers[2], source="3", dest="3")
        self.machine.add_transition(trigger=self.triggers[3], source="3", dest="4")

        # self.machine.add_transition(trigger=self.triggers[0], source="4", dest=")"
        self.machine.add_transition(trigger=self.triggers[1], source="4", dest="1")
        self.machine.add_transition(trigger=self.triggers[2], source="4", dest="3")
        self.machine.add_transition(trigger=self.triggers[3], source="4", dest="4")

        self.machine.add_transition(trigger=self.triggers[0], source="5", dest="8", after='entry')
        self.machine.add_transition(trigger=self.triggers[1], source="5", dest="5")
        self.machine.add_transition(trigger=self.triggers[2], source="5", dest="2")
        self.machine.add_transition(trigger=self.triggers[3], source="5", dest="6")

        # self.machine.add_transition(trigger=self.triggers[0], source="6", dest=")"
        self.machine.add_transition(trigger=self.triggers[1], source="6", dest="5")
        self.machine.add_transition(trigger=self.triggers[2], source="6", dest="2")
        self.machine.add_transition(trigger=self.triggers[3], source="6", dest="6")

        self.machine.add_transition(trigger=self.triggers[0], source="7", dest="7")
        self.machine.add_transition(trigger=self.triggers[1], source="7", dest="1")
        self.machine.add_transition(trigger=self.triggers[2], source="7", dest="2")
        # self.machine.add_transition(trigger=self.triggers[3], source="7", dest=")"

        self.machine.add_transition(trigger=self.triggers[0], source="8", dest="8")
        self.machine.add_transition(trigger=self.triggers[1], source="8", dest="1")
        self.machine.add_transition(trigger=self.triggers[2], source="8", dest="2")
        # self.machine.add_transition(trigger=self.triggers[3], source="8", dest=")"

    def exit(self):
        self.callback(-1)
        # print("Exit!!")
        pass

    def entry(self):
        self.callback(1)
        # print("Entry!!")
        pass


class GridEye(object):

    def __init__(self, callback):
        self.callback = callback

        self.sensor = Adafruit_AMG88xx()
        self.pixels = []
        self.dfa = EntryExitDFA(self.callback)
        # Initiating grid eye sensor
        # Setting 10 FPS
        self.sensor._fpsc.FPS = AMG88xx_FPS_10
        sleep(0.1)
        # print("Initialized Grid Eye")
        self.left_calibration=0
        self.right_calibration=0
        self.verbose = False

        print("Initialized Grid Eye")


    def monitor_temperature(self):
        temp = self.sensor.readThermistor()
        return temp
        
    def read_pixels(self):
        right_pixels = []
        left_pixels = []
        self.pixels = self.sensor.readPixels()
        # print("\nPixels: ", self.pixels)
        right_pixels = self.pixels[:32]
        left_pixels = self.pixels[32:]
        return left_pixels, right_pixels

    def calculate_sum(self):
        left_pixels, right_pixels = self.read_pixels()
        left_sum = 0
        right_sum = 0
        left_sum = sum(left_pixels)
        right_sum = sum(right_pixels)

        return left_sum, right_sum

    def calibrate(self):
        print("Calibrating GridEye..!!")
        left_calibration = 0
        right_calibration = 0

        for i in range(0, 50):
            left_temp, right_temp = self.calculate_sum()
            left_calibration += left_temp
            right_calibration += right_temp
            sleep(0.1)

        left_calibration = 50
        right_calibration = 50

        return left_calibration, right_calibration

    def triggerEvent(self, dfa, sensorL, sensorR):
        if not sensorL and not sensorR:
            return dfa.OO()
        if sensorL and not sensorR:
            return dfa.OI()
        if not sensorL and sensorR:
            return dfa.IO()
        if sensorL and sensorR:
            return dfa.II()

    def calculate_histogram(self):
        right_pixels = []
        left_pixels = []
        
        right_hist = []
        left_hist = []
        hist_bins = [110, 114, 118, 122, 126, 130]
        left_pixels, right_pixels = self.read_pixels()
        
        left_hist = np.histogram(left_pixels[:-8], bins = hist_bins)
        right_hist = np.histogram(right_pixels[8:], bins = hist_bins)

        return left_hist, right_hist

    def monitor_histogram(self):
        # self.left_calibration, self.right_calibration = self.calibrate()
        # print("Left calibration : {0}, Right calibration: {1}".format(self.left_calibration, self.right_calibration))

        while True:
            try:
                left_hist, right_hist = self.calculate_histogram()
                
                # print("Left Values : %d < 118, %d < 122, %d < 126, %d < 130"%(left_hist[0][1], left_hist[0][2], left_hist[0][3], left_hist[0][4]))
                # print("Right Values : %d < 118, %d < 122, %d < 126, %d < 130"%(right_hist[0][1], right_hist[0][2], right_hist[0][3],  right_hist[0][4]))
                
                # print("\nLeft Histogram: ",left_hist)
                # print("Right Histogram:",right_hist[0])
                # print("\n")

                right_list = []
                # right_list = right_hist[0].flip()
                right_list = right_hist[0].tolist()
                left_list = left_hist[0].tolist()
                # print(right_list[::-1])
                # complete_hist =  left_list + right_list[::-1]
                complete_hist = left_list + right_list

                hist_array = np.array(complete_hist)
                
                sum_of_elements = []
                sum_of_elements.append(sum(complete_hist))

                non_zero_elements = []
                non_zero_elements.append(np.count_nonzero(hist_array))

                complete_hist += non_zero_elements
                complete_hist += sum_of_elements

                print("Comeplete histogram : ", complete_hist)

                with open("histogramData.csv", 'a') as file:
                    writer = csv.writer(file)
                    writer.writerow(complete_hist)
                    print("Written to file")

                
                # left_count = left_hist[0][2]
                # right_count = right_hist[0][2]

                # left_sum, right_sum = self.calculate_sum()
                # print("Left sum : {0}, Right sum : {1}".format(left_sum, right_sum))

                # if left_hist[0][1] > 5 or left_hist[0][2] > 2:
                #     sensorL = True
                #     print("Temperature : ", self.monitor_temperature())
                #     print("Left Values : %d < 120, %d < 125, %d < 130\n"%(left_hist[0][1], left_hist[0][2], left_hist[0][3]))
                # else:
                #     sensorL = False

                # if  right_hist[0][1] > 5 or  right_hist[0][2] > 2:
                #     sensorR = True
                #     print("Right Values : %d < session_data["distance_list1"].append(distance1)
                # # session_data["distance_list2"].append(distance2)
                # # session_data["session_count"].append(session_count)120, %d < 125, %d < 130\n"%(right_hist[0][1], right_hist[0][2], right_hist[0][3]))
                # else:
                #     sensorR = False

                # try:
                #     self.triggerEvent(self.dfa, sensorL, sensorR)
                # except:
                #     print("Invalid Event!!")
                #     self.dfa.machine.set_state(self.dfa.machine.initial, model=self.dfa)

            except Exception as e:
                print(str(e))

            sleep(0.1)

    def monitor_sum(self):
        self.left_calibration, self.right_calibration = self.calibrate()
        print("Left calibration : {0}, Right calibration: {1}".format(self.left_calibration, self.right_calibration))
        while True:
            try:
                left_sum, right_sum = self.calculate_sum()
                # print("Left sum : {0}, Right sum : {1}".format(left_sum, right_sum))

                if left_sum > self.left_calibration + 120:
                    sensorL = True
                else:
                    sensorL = False

                if right_sum > self.right_calibration + 120:
                    sensorR = True
                else:
                    sensorR = False

                try:
                    self.triggerEvent(self.dfa, sensorL, sensorR)
                except:
                    print("Invalid Event!!")
                    self.dfa.machine.set_state(self.dfa.machine.initial, model=self.dfa)

                sleep(0.10)
            except Exception as e:
                print("error ge: "+str(e))
   
    def calibrate_ones(self):
        while True:
            self.read_pixels()
            print("Pixels")
            print(np.transpose(np.reshape(self.pixels, [8, 8]) >114).astype(int))
            print("\n")
            sleep(.1)

    def monitor_ones(self):
        self.read_pixels()
        threshold = int(np.mean(np.sort(self.pixels)[-5:]))
        first_direction = 0
        second_direction = 0
        init_pixels_array = np.transpose(np.reshape(self.pixels, [8, 8])).astype(int)
        init_min_pixel = np.min(init_pixels_array)
        init_max_pixel = np.max(init_pixels_array)
        init_mean_pixel = np.mean(init_pixels_array)
        init_std_dev = np.std(init_pixels_array)
        print("Intial Array attributes: Min Value Pixel : %d Max Value Pixel : %d Mean Value Pixel : %d  Std Dev : %d\n"%(init_min_pixel, init_max_pixel, init_mean_pixel, init_std_dev))
        sleep(1)

        while True:
            self.read_pixels()
            # pixels_array = np.transpose(np.reshape(self.pixels, [8, 8]) > threshold+1).astype(int)
            pixels_array = np.transpose(np.reshape(self.pixels, [8, 8])).astype(int)
            right= pixels_array[:,0:3]
            left =pixels_array[:,-3:]

            # print(pixels_array)
            min_pixel = np.min(pixels_array)
            max_pixel = np.max(pixels_array)
            mean_pixel = np.mean(pixels_array)
            std_dev = np.std(pixels_array)

            right_min_pixel = np.min(right)
            right_max_pixel = np.max(right)
            right_mean_pixel = np.mean(right)
            right_std_dev = np.std(right)

            left_min_pixel = np.min(left)
            left_max_pixel = np.max(left)
            left_mean_pixel = np.mean(left)
            left_std_dev = np.std(left)
            # print("Array attributes: Min Value Pixel : %d Max Value Pixel : %d Mean Value Pixel : %d Std Dev : %d\n"%(min_pixel, max_pixel, mean_pixel, std_dev))
            # print("Right attributes: Min Value Pixel : %d Max Value Pixel : %d Mean Value Pixel : %d Std Dev : %d\n"%(right_min_pixel, right_max_pixel, right_mean_pixel, right_std_dev))
            # print("Left  attributes: Min Value Pixel : %d Max Value Pixel : %d Mean Value Pixel : %d Std Dev : %d\n"%(left_min_pixel, left_max_pixel, left_mean_pixel, left_std_dev))

            print("Min Value: Left: %d, Right: %d"%(left_min_pixel, right_min_pixel))
            print("Max Value: Left: %d, Right: %d"%(left_max_pixel, right_max_pixel))
            print("Mean Value:  Left: %d, Right: %d\n"%(left_mean_pixel, right_mean_pixel))

            complete_attributes = []
            # comeplete_attributes.append(min_pixel)
            complete_attributes.append(left_min_pixel)
            complete_attributes.append(right_min_pixel)

            # cmeplete_attributes.append(max_pixel)
            complete_attributes.append(left_max_pixel)
            complete_attributes.append(right_max_pixel)
            
            # cmeplete_attributes.append(mean_pixel)
            complete_attributes.append(left_mean_pixel)
            complete_attributes.append(right_mean_pixel)

            with open("complete_attributes.csv", 'a') as file:
                writer = csv.writer(file)
                writer.writerow(complete_attributes)

        
            all_count = np.count_nonzero(pixels_array[:,1:])
            right_count = np.count_nonzero(right)
            left_count = np.count_nonzero(left)
            
            if self.verbose:
                print("Grid Eye Output:")
                print(pixels_array)
                print("Right count: %d & Left count: %d\n"%(np.count_nonzero(right), np.count_nonzero(left)))
            # print("right:\n",pixels_array[:,0:3],"\nleft:\n",pixels_array[:,-3:],"\n")

            # print("All count", all_count)
            # print("Left count", left_count)
            # print("Right count", right_count)
            # print("")

            if all_count>12:
                if first_direction == 0:
                    if left_count - right_count > 5 or left_count - right_count < -5:
                        first_direction = left_count - right_count
                        # print("Set first_direction : ", first_direction)
                else:
                    second_direction = left_count - right_count
                    # print("Set second_direction", second_direction)
            else:
                if first_direction < 0 and second_direction < 0:
                    print("Bhag gaya :D")
                elif first_direction < 0 and second_direction > 0:
                    self.callback(1)
                elif first_direction > 0 and second_direction < 0:
                    self.callback(-1)
                elif first_direction > 0 and second_direction > 0:
                    print("Andar aa gaya :D")

                first_direction = 0
                second_direction = 0

            sleep(0.05)
            

    def monitor(self):
        # self.monitor_histogram()
        self.monitor_ones()