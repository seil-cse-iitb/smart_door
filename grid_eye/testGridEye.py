# from fsm_with_grid_eye import GridEye as ge
from GridEye import GridEye as ge
import time 
def test(event):
    print(time.asctime()," : ",event)

ge_object = ge(test)
# ge_object.monitor()

ge_object.monitor()