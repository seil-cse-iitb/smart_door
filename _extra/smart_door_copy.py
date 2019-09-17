import glob
import sys
from threading import Thread, Lock
import time
import requests
import serial
import json
# from mqtt_handler import mqttHandler as MQTT

from tof.ToF import ToF
from weight_mat.WeightMat import WeightMat as WM
from grid_eye.GridEye import GridEye as GE
from ultrasonic.Ultrasonic import Ultrasonic as US

id_list = [0, 0, 0]
ts_list = [0, 0, 0]
ge_status = 0
wm_status = [0, 0]
us_status = 0
ts_init = False
ts = 0
kill_time_thread = False

appliance_dict = {
    "17" : [],
    "18" : [],
    "19" : [],
    "20" : [],
    "21" : [],
    "22" : [],
    "23" : [],
    "24" : [],
    "25" : [],
    "26" : []
}

def time_monitor():
    global ts
    global kill_time_thread
    global ts_init

    print("Started timer thread at : ", time.asctime())
    while not kill_time_thread:
        if int(time.time()) - ts < 2:
            continue
        else:
            print("False timer tigger")
            id_list = [0, 0, 0]
            ts_list = [0, 0, 0]
            break

    kill_time_thread = False
    ts_init = False
    # print("End of TS monitor")
    return 0


def timer_interrupt():
    global ts_init
    global ts

    if not ts_init:
        ts = int(time.time())
        ts_init = True
        timer_thread = Thread(target=time_monitor)
        timer_thread.start()

def events_check(id):
    global id_list

    is_equal = True
    ts_match = True
    id_list[id - 1] = 1

    for i in range(0, len(id_list)):
        if id_list[i] != 1:
            is_equal = False
            break

    return is_equal


def ge_callback(entry_exit):
    global ge_status
    global kill_time_thread

    id = 1
    if entry_exit == 1:
        entry_exit_status = "entry"
    elif entry_exit == -1:
        entry_exit_status = "exit"
    else:
        entry_exit_status = "invalid event (GridEye)"
    # print("Event: ", entry_exit_status)

    ge_status = entry_exit

    timer_interrupt()

    if events_check(id):
        kill_time_thread = True
        event_monitor()

def wm_callback(weight, steps):
    global wm_status
    global kill_time_thread

    id = 2
    print("Weight: ", weight, " Steps: ", steps)

    wm_status[0] = weight
    wm_status[1] = steps

    timer_interrupt()

    if events_check(id):
        kill_time_thread = True
        event_monitor()


def tof_callback(height):
    # print("Height: ", distance)

    global us_status
    global kill_time_thread

    id = 3
    print("Height: ", height)
    us_status = height

    timer_interrupt()

    if events_check(id):
        kill_time_thread = True
        event_monitor()

def actuate_appliances(user, direction):
    # global mqtt
    global appliance_dict
    # mqtt_topic = "actuation/kresit/2/213/"
    actuation_url = "http://10.129.149.33:1337/equipment/actuate/"

    with open('appliances_mapping.json') as config:
        data = json.load(config)
    
    #  for key, value in appliance_dict:
    for appliances in appliance_dict:
        # print appliances
        if user in data[appliances]:
            if direction == 'entry' and not (user in appliance_dict[appliances]):
                appliance_dict[appliances].append(user)
            elif direction == 'exit':
                if len(appliance_dict[appliances]):
                    try:
                        appliance_dict[appliances].remove(user)
                    except Exception as e:
                        print(e)
        
        # print len(appliance_dict[appliances])
        if len(appliance_dict[appliances]) != 0:
            print(actuation_url + appliances + "/ : " + "S1")
            # mqtt.on_publish(appliances, "S1")
            requests.post(url = actuation_url + appliances, data = json.dumps({"msg":"S1","state":True}))
        elif len(appliance_dict[appliances]) == 0:
            print(actuation_url + appliances + "/ : " + "S0")
            # mqtt.on_publish(appliances, "S0")
            requests.post(url = actuation_url + appliances, data = json.dumps({"msg":"S0","state":False}))

def get_request_url(url, direction):
    response = requests.get(url)
    if (response.status_code == 200):
        
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

def send_to_server(weight, steps, height, direction):  # weight,steps,height
    server_root = "http://10.129.149.33:5000/api"
    url = server_root + '/prediction/' + str(height) + "/" + str(weight) + "/" + str(steps) + "/" + str(direction)
    Thread(target=get_request_url, args=(url, direction)).start()


def event_monitor():
    global id_list
    global ts_list
    global ge_status
    global us_status
    global wm_status
    global kill_time_thread

    if kill_time_thread:
        print("\n A complete event with:")
        print("\t Event: ", ge_status)
        print("\t Weight: %d and Steps: %d" % (wm_status[0], wm_status[1]))
        print("\t Height: ", us_status)
        print("\n")
        kill_time_thread = True
        is_equal = False
        ge_str = "fault(GE)"
        if ge_status == 1:
            ge_str = "entry"
        elif ge_status == -1:
            ge_str = "exit"
        send_to_server(wm_status[0], wm_status[1], us_status, ge_str)
    id_list = [0, 0, 0]
    ts_list = [0, 0, 0]


def serial_port():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
        return result


if __name__ == "__main__":

    port = "ttyUSB0"
    # for ports in serial_port():
    #     if ports[5:11] == "ttyACM":
    #         print("Found Arduino", ports)
    #         port = ports[5:]

    weight_serial_name = port
    # print(weight_serial_name)
    tof = ToF(tof_callback)
    ge = GE(ge_callback)
    wm = WM(weight_serial_name, wm_callback)

    # tof.verbose = True
    # wm.verbose = True
    # ge.verbose = True

    tof_thread = Thread(target=tof.monitor)
    tof_thread.start()

    ge_thread = Thread(target=ge.monitor)
    ge_thread.start()

    wm_thread = Thread(target=wm.monitor)
    wm_thread.start()

    wm_thread.join()
    tof_thread.join()
    ge_thread.join()
