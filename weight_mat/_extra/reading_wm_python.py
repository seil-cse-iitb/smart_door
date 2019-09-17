from hx711_g import HX711
import RPi.GPIO as GPIO
import time

weight_value = 0

try:
    hx = HX711(dout_pin=20, pd_sck_pin=21, gain_channel_A=128)

    result = hx.reset()
    if result:
        print("Ready to take weight on its shoulders")
    else:
        print("Nada")

    data = hx.get_raw_data_mean(times=3)
    if data != False:
        print("Raw data: "+ str(data))
    else:
        print("Invalid data")
    
    result = hx.zero(times=10)

    data = hx.get_data_mean(times=10)

    if data != False:
        print("Processed data : " + str(data))
    else:
        print("Invalid data")
    
    input('Put known weight and pres Enter')

    data = abs(hx.get_data_mean(times=10))

    if data != False:
        print("Mean value of weight : " + str(data))
        known_weight = input("What was the actual weight?")

        try:
            value = float(known_weight)
            print(str(value) + "kgs")
        except ValueError:
            print(ValueError)
        
        ratio = data / value
        hx.set_scale_ratio(scale_ratio=ratio)
        print("Ratio is ", ratio)
    else:
        print("Some random error")

    print("Current weight on the scale is " + str(hx.get_weight_mean(times=10)))

    input("Ask someone to stand on it")
    for i in range(40):
        print(str(hx.get_weight_mean(times=10)))
finally:
    print("bbye")