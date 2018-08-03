from transitions import *
import random
import re
from time import *
from Adafruit_AMG88xx import *
import sys

class gridEye(object):

    sensor = Adafruit_AMG88xx()
    pixels = []
    # right_pixels = []
    # left_pixels = []

    def __init__(self):
        # Initiating grid eye sensor
        # Setting 10 FPS
        self.sensor._fpsc.FPS = AMG88xx_FPS_10
        sleep(0.1)
        print("Initialized Grid Eye")

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
        print "Calibrating..!!"
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

class entryExitDFA(object):
    states = ["0","1","2","3","4","5","6","7","8","9"]
    
    triggers =["OO","OI","IO","II"] #[0,1,2,3] #["00","01","10","11"]
    
    def __init__(self):
        print("DFA init!")
      
        self.machine = Machine(model=self, states=entryExitDFA.states, initial="0")
      
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

        self.machine.add_transition(trigger=self.triggers[0], source="3", dest="7", after='entry')
        self.machine.add_transition(trigger=self.triggers[1], source="3", dest="1")
        self.machine.add_transition(trigger=self.triggers[2], source="3", dest="3")
        self.machine.add_transition(trigger=self.triggers[3], source="3", dest="4")

        # self.machine.add_transition(trigger=self.triggers[0], source="4", dest=")"
        self.machine.add_transition(trigger=self.triggers[1], source="4", dest="1")
        self.machine.add_transition(trigger=self.triggers[2], source="4", dest="3")
        self.machine.add_transition(trigger=self.triggers[3], source="4", dest="4")

        self.machine.add_transition(trigger=self.triggers[0], source="5", dest="8", after='exit')
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
        print("Exit!!")
        pass

    def entry(self):
        print("Entry!!")
        pass

class entryExitEvent(object):
    # States for entry/exit system
    # states = ['haq se single', 'pahle ka kata', 'dono ka kata', 'dusre ka kata']
    states = ['no_cut', 'first_cut', 'both_cut', 'second_cut']
    transition_string = "0"
    # test_string = "0132"
    occupancy_count = 0;
    entry_pattern = r'(0*)(1*)(3*)(2*)'
    exit_pattern = r'(0*)(2*)(3*)(1*)'

    def __init__(self):

        print("Inside fsm init")

        self.machine = Machine(model=self, states=entryExitEvent.states, initial=self.states[0])

        # Multiple transitions in the state
        # When the first laser is cut
        self.machine.add_transition(trigger='first_triggered', source=self.states[0], dest=self.states[1]) #, after='entering_state_1')
        # When both lasers are cut
        self.machine.add_transition(trigger='second_triggered', source=self.states[1], dest=self.states[2]) #, after='entering_state_3')
        # When only second is cut and first one is not
        self.machine.add_transition(trigger='first_halted', source=self.states[2], dest=self.states[3]) #, after='entering_state_2')
        # When none are cut
        self.machine.add_transition(trigger='second_halted', source=self.states[3], dest=self.states[0]) #, after='entering_state_0')

        self.machine.add_transition(trigger='second_triggered', source=self.states[0], dest=self.states[3]) #, after='entering_state_2')
        self.machine.add_transition(trigger='first_triggered', source=self.states[3], dest=self.states[2]) #, after='entering_state_3')
        self.machine.add_transition(trigger='second_halted', source=self.states[2], dest=self.states[1])#, after='entering_state_1')
        self.machine.add_transition(trigger='first_halted', source=self.states[1], dest=self.states[0]) #, after='entering_state_0')

    def on_enter_no_cut(self):
        print("Entering state 0")
        print(self.transition_string)
        try:
            entry_pattern_obj = re.search(self.entry_pattern, self.transition_string)
            entry_pattern_list = []
            entry_pattern_list = list(entry_pattern_obj.groups())
            if(len(entry_pattern_list) == 4):
                print "Entry event"
                self.occupancy_count += 1
        except Exception as e:
            print e

        try:
            exit_pattern_obj = list(re.search(self.exit_pattern, self.transition_string))
            exit_pattern_list = []
            exit_pattern_list = list(exit_pattern_obj.groups)
            if(len(exit_pattern_list) == 4):
                print "Exit event"
                self.occupancy_count -= 1

        except Exception as e:
            print e
        self.transition_string = "0"
        
    def on_enter_first_cut(self):
        self.transition_string += "1"
        print("Entering state 1")

    def on_enter_second_cut(self):
        self.transition_string += "2"
        print("Entering state 2")

    def on_enter_both_cut(self):
        self.transition_string += "3"
        print("Entering state 3")

        
def triggerEvent(dfa,sensorL,sensorR):
    if not sensorL and not sensorR:
        return dfa.OO()
    if sensorL and not sensorR:
        return dfa.OI()
    if not sensorL and sensorR:
        return dfa.IO()
    if sensorL and sensorR:
        return dfa.II()

    

if __name__ == '__main__':

    states = entryExitEvent()
    # lump = entryExitEvent()
    # lump.second_triggered()
    # lump.first_triggered()
    # lump.first_halted()
    # lump.second_halted()    

    dfa = entryExitDFA()
    sensorL=False
    sensorR=False

    grid_eye_obj = gridEye()
    
    left_calibration, right_calibration = grid_eye_obj.calibrate()
    print("Left calibration : {0}, Right calibration: {1}".format(left_calibration, right_calibration))

    first_triggered = False
    second_triggered = False

    try:
        while(True):

            # left_data, right_data = grid_eye_obj.read_pixels()
            left_sum, right_sum = grid_eye_obj.calculate_sum()
            # print("Left sum : {0}, Right sum : {1}".format(left_sum, right_sum))

            if left_sum > left_calibration + 100:
                sensorL=True
                if not first_triggered:
                    print "Left Sensor triggered"
                    # states.first_triggered()
                    # first_triggered = True
            else:
                sensorL=False
                if first_triggered:
                    print "Left Sensor halted"
                #     states.first_halted()
                #     first_triggered = False
                # pass

            if right_sum > right_calibration + 100:
                sensorR=True
                if not second_triggered:
                    print "Right Sensor triggered"
                #     states.second_triggered()
                #     second_triggered = True
            else:
                sensorR=False
                if second_triggered:
                    print "Right Sensor halted"
                #     states.second_halted()
                #     second_triggered = False
                # pass
            
            triggerEvent(dfa,sensorL,sensorR)
            
            sleep(0.10)
        
    except KeyboardInterrupt:
        print "Stopped program manually"
        sys.exit()
