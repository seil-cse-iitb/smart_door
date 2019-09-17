# from ToF import ToF
# from multipleToF import ToF
from MultiToF import ToF

def test(value):
    print(value)
    pass

xshut_pins = [4, 17]
addresses = [0x2B, 0x2D]
is_multiple_tof = True
tof = ToF(xshut_pins, addresses, is_multiple_tof, test, test)
tof.verbose = True
tof.test()

# tof.monitor()

# if tof.calibrate():
#     print(tof.door_height)
# else:
#     print("calibration failed!!")
