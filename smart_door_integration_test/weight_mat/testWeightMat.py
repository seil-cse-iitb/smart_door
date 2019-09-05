from WeightMat import *


def weight_session_callback(weight,steps):
    print("weight callback! weight: "+str(weight)+"kg steps: "+str(steps))
    pass

def event_handler(para):
    pass
weight_serial_name = "ttyUSB0"

WM = WeightMat(weight_serial_name, weight_session_callback,event_handler)
WM.set_verbose(False)
WM.test()
