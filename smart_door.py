from threading import Thread

from tof.ToF import ToF
from weight_mat.WeightMat import WeightMat as WM
from entry_exit_test.fsm_with_grid_eye import GridEye as GE
from ultrasonic.Ultrasonic import Ultrasonic as US


def ge_callback(entry_exit):
    if entry_exit == 1:
        entry_exit_status = "entry"
    elif entry_exit == -1:
        entry_exit_status = "exit"
    else:
        entry_exit_status = "invalid event (GridEye)"
    print("Event: ", entry_exit_status)


def wm_callback(weight, steps):
    print("Weight: ", weight, " Steps: ", steps)


def tof_callback(distance):
    print("Height: ", distance)

def us_callback(height):
    print("Height: ", height)

weight_serial_name = "ttyUSB0"

tof = ToF(tof_callback)
wm = WM(weight_serial_name, wm_callback)
ge = GE(ge_callback)
us = US(17,4,80,us_callback)

# tof.verbose = True
# wm.verbose = True

us_thread = Thread(target=us.monitor)
us_thread.start()

ge_thread = Thread(target=ge.monitor)
ge_thread.start()

tof_thread = Thread(target=tof.monitor)
# tof_thread.start()

wm_thread = Thread(target=wm.monitor)
wm_thread.start()

tof_thread.join()
wm_thread.join()
ge_thread.join()
us_thread.join()