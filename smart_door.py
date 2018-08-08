from threading import Thread

from tof.ToF import ToF
from weight_mat.WeightMat import WeightMat as WM


def tof_callback(distance):
    pass
def wm_callback(weight,steps):
    print(weight,steps," Inside callback")
    pass

weight_serial_name = "ttyUSB0"

tof = ToF(tof_callback)
wm = WM(weight_serial_name,wm_callback)
wm.set_verbose(True)

tof_thread=Thread(target = tof.monitor)
tof_thread.start()

wm_thread = Thread(target= wm.monitor)
wm_thread.start()

tof_thread.join()
wm_thread.join()

