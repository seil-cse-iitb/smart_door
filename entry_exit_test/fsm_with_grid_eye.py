from transitions import *
import random
import re
from time import *
from Adafruit_AMG88xx import *
import sys


class EntryExitDFA(object):
    states = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    triggers = ["OO", "OI", "IO", "II"]  # [0,1,2,3] #["00","01","10","11"]

    def __init__(self, callback):
        self.callback = callback
        print("DFA init!")

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
        print("Initialized Grid Eye")

        self.left_calibration, self.right_calibration = self.calibrate()
        print("Left calibration : {0}, Right calibration: {1}".format(self.left_calibration, self.right_calibration))

    def read_pixels(self):
        right_pixels = []
        left_pixels = []
        self.pixels = self.sensor.readPixels()
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
        print("Calibrating..!!")
        left_calibration = 0
        right_calibration = 0

        for i in range(0, 50):
            left_temp, right_temp = self.calculate_sum()
            left_calibration += left_temp
            right_calibration += right_temp
            sleep(0.1)

        left_calibration /= 50
        right_calibration /= 50

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

    def monitor(self):

        while True:
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
