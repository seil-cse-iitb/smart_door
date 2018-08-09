from transitions import *
import random
import re

class entryExitEvent(object):
    # States for entry/exit system
    states = ['haq se single', 'pahle ka kata', 'dono ka kata', 'dusre ka kata']
    #  states = ['no cut', 'first cut', 'both cut', 'second cut']
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
        self.machine.add_transition(trigger='first_triggered', source=self.states[0], dest=self.states[1], after='entering_state_1')
        # When both lasers are cut
        self.machine.add_transition(trigger='second_triggered', source=self.states[1], dest=self.states[2], after='entering_state_3')
        # When only second is cut and first one is not
        self.machine.add_transition(trigger='first_halted', source=self.states[2], dest=self.states[3], after='entering_state_2')
        # When none are cut
        self.machine.add_transition(trigger='second_halted', source=self.states[3], dest=self.states[0], after='entering_state_0')

        self.machine.add_transition(trigger='second_triggered', source=self.states[0], dest=self.states[3], after='entering_state_2')
        self.machine.add_transition(trigger='first_triggered', source=self.states[3], dest=self.states[2], after='entering_state_3')
        self.machine.add_transition(trigger='second_halted', source=self.states[2], dest=self.states[1], after='entering_state_1')
        self.machine.add_transition(trigger='first_halted', source=self.states[1], dest=self.states[0], after='entering_state_0')

    def entering_state_0(self):
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
        # # self.transition_string = "0"
        


    def entering_state_1(self):
        self.transition_string += "1"
        print("Entering state 1")

    def entering_state_2(self):
        self.transition_string += "2"
        print("Entering state 2")

    def entering_state_3(self):
        self.transition_string += "3"
        print("Entering state 3")

        
if __name__ == '__main__':

    lump = entryExitEvent()
    lump.second_triggered()
    lump.first_triggered()
    lump.first_halted()
    lump.second_halted()    