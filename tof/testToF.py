from ToF import ToF
# from multipleToF import ToF

def test(value):
    print(value)
    pass

tof = ToF(test)
tof.verbose = True
tof.test()

# tof.monitor()


# if tof.calibrate():
#     print(tof.door_height)
# else:
#     print("calibration failed!!")
