from WeightMat import *


def weight_session_callback(record):
    print("weight callback!")
    pass

weight_serial_name = "ttyUSB0"

WM = WeightMat(weight_serial_name, weight_session_callback)
WM.set_verbose(True)
WM.monitor()
