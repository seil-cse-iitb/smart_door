from hx711_g import HX711
import RPi.GPIO as GPIO

hx = HX711(dout_pin=20, pd_sck_pin=21, gain_channel_A=64)

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

print(hx.get_current_channel())
print(hx.get_current_gain_A)

while True:
    result = hx.zero(times=1)
    print("----", result)
    data = hx.get_data_mean()
    print("Raw Data is ", data)