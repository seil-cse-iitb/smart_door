from threading import Thread

from tof.ToF import ToF
from weight_mat.WeightMat import WeightMat as WM
from entry_exit_test.fsm_with_grid_eye import GridEye as ge


def ge_callback(entry_exit_status):
    print(entry_exit_status)

def wm_callback(weight,steps):
    print(weight,steps," Inside callback")

def tof_callback(distance):
    pass


weight_serial_name = "ttyUSB0"

tof = ToF(tof_callback)
wm = WM(weight_serial_name,wm_callback)
wm.set_verbose(True)
ge = ge(ge_callback)

ge_thread = Thread(target = ge.monitor)
ge_thread.start()

tof_thread=Thread(target = tof.monitor)
tof_thread.start()

wm_thread = Thread(target= wm.monitor)
wm_thread.start()

tof_thread.join()
wm_thread.join()

