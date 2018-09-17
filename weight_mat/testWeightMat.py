from WeightMat import *


def weight_session_callback(weight,steps):
    print("weight callback!"+str(weight)+" "+str(steps))
    pass

weight_serial_name = "ttyACM0"

WM = WeightMat(weight_serial_name, weight_session_callback)
WM.set_verbose(True)
WM.monitor()
