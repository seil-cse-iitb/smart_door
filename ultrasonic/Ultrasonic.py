import time
from statistics import median

from hcsr04sensor import sensor
from threading import Thread, Timer
import RPi.GPIO as GPIO

# Created by Al Audet
# MIT License

GPIO.setmode(GPIO.BCM)


class Ultrasonic:
    def __init__(self, trigger_pin, echo_pin,limit,callback):
        self.id = ""
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.pulse_start = 0
        self.pulse_end = 0
        self.pulse_duration = 0
        self.echo_state = 1
        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.echo_pin, GPIO.BOTH, callback=self.echo_handler)

        self.limit = limit
        self.reading_count = 0
        self.distance_list = []
        self.callback = callback
        self.session=False
        self.session_counter=0
        self.verbose =False


    # def sense(self):
    #     value = sensor.Measurement(self.trigger_pin, self.echo_pin)
    #     raw_measurement = value.raw_distance(sample_size=1)
    #     metric_distance = value.distance_metric(raw_measurement)
    #     # print(self.id, " ", end='')
    #     return metric_distance

    def trigger(self):
        while True:
            GPIO.output(self.trigger_pin, False)
            time.sleep(0.00005)
            GPIO.output(self.trigger_pin, True)
            time.sleep(0.00005)
            GPIO.output(self.trigger_pin, False)
            time.sleep(0.03)

    def monitor(self):
        try:
            GPIO.output(self.trigger_pin, False)
            print("Waiting For Sensor To Settle")
            time.sleep(2)
            print("Sensor ready")
            self.trigger()
        finally:
            print("cleaning up")
            GPIO.cleanup()


    def echo_handler(self, channel):
        if self.echo_state == 1:  # falling edge detected
            self.pulse_start = time.time()
            self.echo_state = 2  # level low
        elif self.echo_state == 2:  # rising edge detected
            self.pulse_end = time.time()
            self.pulse_duration = self.pulse_end - self.pulse_start
            self.echo_state = 1

            distance = self.pulse_duration * 17150
            distance = round(distance, 2)
            # print( self.id," Distance:",distance,"cm")

            if 11 <= distance <= self.limit:
                self.session = True
                self.session_counter=5
                if self.verbose:
                    print("%d mm, %d cm, %d" % (distance, (distance / 10), self.reading_count))
                self.distance_list.append(distance)
                self.reading_count += 1
            elif distance<11:
                pass
            else:
                if self.session:
                    if self.session_counter>0:
                        self.session_counter-=1
                    else:
                        self.session = False
                        # print("Session completed: ", (person_distance / reading_count))
                        if self.verbose:
                            print("Session completed: min:", min(self.distance_list))
                        self.callback(median(self.distance_list))
                        self.distance_list = []
                        self.reading_count = 0

