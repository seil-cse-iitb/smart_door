from threading import Thread
import time
import requests
from tof.ToF import ToF
from weight_mat.WeightMat import WeightMat as WM
# from entry_exit_test.fsm_with_grid_eye import GridEye as GE
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

def time_monitor():
    global ts
    global kill_time_thread
    global ts_init

    print("Started timer thread at ", ts)
    while not kill_time_thread:
        if int(time.time()) - ts < 10:
            continue
        else:
            print("False timer tigger")
            id_list = [0, 0, 0]
            ts_list = [0, 0, 0]
            break
            
    kill_time_thread = False
    ts_init = False
    print("End of TS monitor")
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
    id_list[id-1] = 1

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
    print("Event: ", entry_exit_status)

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

def us_callback(height):
    global us_status
    global kill_time_thread

    id = 3
    print("Height: ", height)
    us_status = height

    timer_interrupt()

    if events_check(id):
        kill_time_thread = True
        event_monitor()


def get_request_url(url):
    response = requests.get(url)
    if (response.status_code == 200):
        print("Successfully sent=> ", url)
    else:
        print("Failed to sent=> ", url)
        print("Response: ", response)

def send_to_server(weight, steps, height, direction):  # weight,steps,height
    server_root="http://10.129.149.33:5000/api"
    url = server_root + '/prediction/' + str(height) + "/" + str(weight) + "/" + str(steps) + "/" + str(direction)
    Thread(target=get_request_url, args=(url,)).start()

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
        print("\t Weight: %d and Steps: %d"%(wm_status[0], wm_status[1]))
        print("\t Height: ", us_status)
        print("\n")
        kill_time_thread = True
        is_equal = False
        ge_str="fault(GE)"
        if ge_status==1:
            ge_str = "entry"
        elif ge_status==-1:
            ge_str= "exit"
        send_to_server(wm_status[0],wm_status[1],us_status,ge_str)
    id_list = [0, 0, 0]
    ts_list = [0, 0, 0]

if __name__ == "__main__":

    weight_serial_name = "ttyUSB0"

    tof = ToF(tof_callback)
    wm = WM(weight_serial_name, wm_callback)
    ge = GE(ge_callback)
    # us = US(17,4,70,us_callback)

    # tof.verbose = True
    # wm.verbose = True
    # us.verbose = True
    
    # us_thread = Thread(target=us.monitor)
    # us_thread.start()

    ge_thread = Thread(target=ge.monitor)
    ge_thread.start()

    tof_thread = Thread(target=tof.monitor)
    tof_thread.start()

    wm_thread = Thread(target=wm.monitor)
    wm_thread.start()

    # em_thread = Thread(target= event_monitor)
    # em_thread.start()

    tof_thread.join()
    # us_thread.join()
    ge_thread.join()
    wm_thread.join()
    # em_thread.join()