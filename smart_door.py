import glob
import sys
from threading import Thread, Lock
import time
import requests
import serial
import json
# from mqtt_handler import mqttHandler as MQTT
# from tof.ToF import ToF
from tof.MultiToF import ToF
from grid_eye.GridEye import GridEye as GE
from weight_mat.WeightMat import WeightMat as WM

server_root = "http://10.129.149.32:5000/api"

def get_request_url(url, direction):
    response = requests.get(url)
    if response.status_code == 200:
        predicted_content = str(response.content)
        user = []
        user = predicted_content.split("'")
        print("Successfully sent=> ", url)
        print("Prediction	=> ", user[1])
        if len(user[1]) > 0:
            print(user[1])
            # actuate_appliances(user[1], direction)
    else:
        print("Failed to sent=> ", url)
        print("Response: ", response)
    print("--------------")
    print()


def send_to_server(weight, steps, height, direction):  # weight,steps,height
    global server_root
    str_direction = ""
    if direction ==  1 :
        str_direction = "entry"
    elif direction == -1 :
        str_direction = "exit"
    url = server_root + '/prediction/' + str(height) + "/" + str(weight) + "/" + str(steps) + "/" + str(str_direction)
    Thread(target=get_request_url, args=(url, direction)).start()


def event_handler(sensor):
    global tof, ge, wm
    print(time.asctime(), ": Event is changed by", sensor.name, "and the status is", sensor.get_status())
    if tof.get_status() == "COMPLETED" and ge.get_status() == "COMPLETED" and wm.get_status() == "COMPLETED":
        print("Event Completed!")
        if tof.is_data_ok() and ge.is_data_ok() and wm.is_data_ok():
            print("Data OK!")
            print("TOF:", tof.height, "GE:", ge.event, "WM:weight->", wm.weight, "steps->", wm.steps)
            send_to_server(wm.weight, wm.steps, tof.height, ge.event)
        else:
            print("Data not OK!", tof.is_data_ok(), ge.is_data_ok(), wm.is_data_ok())
        print("Reset TOF,GE,WM\n\n\n")
        tof.height = None
        tof.status = "READING"
        ge.event = None
        ge.status = "READING"
        wm.weight = None
        wm.steps = None
        wm.status = "READING"
        # tof.reset_status_and_data()
        # ge.reset_status_and_data()
        # wm.reset_status_and_data()
    else:
        # mutex.acquire()
        tof_status = status_to_int(tof.get_status())
        ge_status = status_to_int(ge.get_status())
        wm_status = status_to_int(wm.get_status())
        if tof_status is None or ge_status is None or wm_status is None:
            print("Sensor with undefined status::TOF:", tof.get_status(), "GE:", ge.get_status(), "WM:",
                  wm.get_status())
            # print("Reset TOF,GE,WM")
            # tof.reset_status_and_data()
            # ge.reset_status_and_data()
            # wm.reset_status_and_data()
        elif ((tof_status + ge_status + wm_status == 4) and (tof_status == 0 or ge_status == 0 or wm_status == 0)) \
                or (
                (tof_status + ge_status + wm_status == 2) and (tof_status == 2 or ge_status == 2 or wm_status == 2)):
            print("Event could not complete! Status::TOF:", tof.get_status(), "GE:", ge.get_status(), "WM:",
                  wm.get_status())
            print("Reset TOF,GE,WM\n\n\n")
            tof.height = None
            tof.status = "READING"
            ge.event = None
            ge.status = "READING"
            wm.weight = None
            wm.steps = None
            wm.status = "READING"
            # tof.reset_status_and_data()
            # ge.reset_status_and_data()
            # wm.reset_status_and_data()
        # mutex.release()


def status_to_int(str):
    if str == "READING":
        return 0
    elif str == "TRIGGERED":
        return 1
    elif str == "COMPLETED":
        return 2
    else:
        return None


def ge_callback(event):
    print(time.asctime(), ": Grid Eye::", event)


def tof_callback(height):
    print(time.asctime(), ": TOF::", height)


def wm_callback(weight, steps):
    print(time.asctime(), ": WM::weight:", weight, ", steps:", steps)


if __name__ == "__main__":
    global tof, ge, wm
    port = "ttyUSB0"
    weight_serial_name = port

    xshut_pins = [4, 17]
    addresses = [0x2B, 0x2D]
    is_multiple_tof = True

    tof = ToF(xshut_pins, addresses, is_multiple_tof, tof_callback, event_handler)
    ge = GE(ge_callback, event_handler)
    wm = WM(weight_serial_name, wm_callback, event_handler)
    ge.set_server_root(server_root)

    tof.verbose = False
    wm.verbose = False
    ge.verbose = False

    tof_thread = Thread(target=tof.monitor)
    tof_thread.start()
    
    ge_thread = Thread(target=ge.monitor)
    ge_thread.start()
    
    wm_thread = Thread(target=wm.monitor)
    wm_thread.start()
    
    wm_thread.join()
    tof_thread.join()
    ge_thread.join()
