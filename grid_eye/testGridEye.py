# from fsm_with_grid_eye import GridEye as ge
# from GridEye import GridEye as ge
from GridEyeAnalysis import GridEye as ge
import time

sensor_id = "grideye_k_seil_1"
count = 0

def test(event):
    global count
    if count == 0 and event == -1:
        count == 0
    else:
        count += event
    
    print(time.asctime()," : ", event, " : ", count)
    

ge_object = ge(sensor_id, test)
# ge_object.monitor()
ge_object.verbose = False
ge_object.monitor()
