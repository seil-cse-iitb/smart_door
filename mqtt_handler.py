import paho.mqtt.client as mqtt
import paho.mqtt.client as client
from threading import Thread
from time import sleep

class mqttHandler(object):

    MQTT_HOST = "10.129.149.9"
    MQTT_PORT = 1883
    MQTT_CLIENT = "SmartDoor_rpi"
    # MQTT_TOPIC_GRID_EYE = "rpi/smart_door/grid_eye_data"
    # MQTT_TOPIC_TOF = "rpi/smart_door/tof_data"
    # MQTT_TOPIC_WEIGHT_MAT = "rpi/smart_door/weight_mat"
    # MQTT_TOPIC = "rpi/smart_door/data"
    MQTT_TOPIC = 'actuation/kresit/2/213/'
    client = mqtt.Client(MQTT_CLIENT)

    def __init__(self):
        ## Initializer
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.MQTT_HOST, self.MQTT_PORT, 6)
        connection_thread = Thread(target = self.client.loop_forever)
        connection_thread.start()

    def on_connect(self,client, userdata, flags, rc):
        print("Connected to MQTT with result " + str(rc))

    def on_message(self, client, userdata, msg):
        print("%s : %s : %d" %(msg.topic, msg.payload, len(msg.payload)))

    def on_publish(self, appliance, data):
        print("Inside publish")
        self.client.publish(self.MQTT_TOPIC + appliance + "/", data)

if __name__ == "__main__":

    mqtt_handler = mqttHandler()