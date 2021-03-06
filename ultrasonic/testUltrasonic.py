from Ultrasonic import Ultrasonic
from threading import Thread, Timer


def h1_callback(distance):
    print("Height: ", distance)


h1 = Ultrasonic(17, 4, 80, h1_callback)
h1.verbose = True
thread1 = Thread(target=h1.monitor)
thread1.start()
thread1.join()
