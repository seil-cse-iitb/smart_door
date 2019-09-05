import paho.mqtt.client as mqtt
import paho.mqtt.client as publish
import time
import datetime as dt
import threading
import variable

MQTT_HOST = '10.129.149.64'
MQTT_PORT = 1883
MQTT_CLIENT = "RPI_205"

MQTT_TOPIC_AC = 'nodemcu/SCC/AC'        #Topic for publishing to ACs
MQTT_TOPIC_LF = 'nodemcu/SCC/LF'        #Topic for publishing to Lights and fans
MQTT_TOPIC_PIR = 'nodemcu/SCC/PIR'      #Topic which subscribes to the PIR status
MQTT_TOPIC_SSS = 'nodemcu/SCC/SSS'      #Topic which subscribes to the SSS
MQTT_TOPIC_AC_BACK = 'nodemcu/SCC/AC_BACK'
MQTT_TOPIC_LF_BACK = 'nodemcu/SCC/LF_BACK'

client = mqtt.Client(MQTT_CLIENT)

pirState = False
flag = 0

def subscribeToPIR():
	client.subscribe(MQTT_TOPIC_PIR, qos=1)

def unsubscribeToPIR():
	client.unsubscribe(MQTT_TOPIC_PIR)

def on_connect(client, userdata, flags, rc):
	print "Connected to MQTT with result " + str(rc)
	client.subscribe(MQTT_TOPIC_SSS, qos=1)

def on_message(client, userdata, msg):
	global pirState
	global flag

	print ("%s : %s : %d" %(msg.topic, msg.payload, len(msg.payload)))

	if msg.topic == MQTT_TOPIC_PIR:
		#print "Message Received from PIR topic"
		if msg.payload == "PIR1":
			pirState = True
			flag = 1
			print "Changed PIR Status to " + str(variable.pir_state)
			print "pir sense things " + str(variable.pir_sense)
			publishData("L0", 1)
		else:
			pirState = False
	elif msg.topic == MQTT_TOPIC_SSS:
		variable.mqttButtonStatus = msg.payload
		print "SSS is " + variable.mqttButtonStatus

def publishData(appliance_id, command):
	if appliance_id[0] == 'F':
		msg = 'F ' + str(command)
		client.publish(MQTT_TOPIC_LF, msg, 1)
		print "**** Published " + msg + " to Fans ****"
	elif appliance_id[0] == 'L':
		msg = 'L ' + str(command)
		client.publish(MQTT_TOPIC_LF, msg, 1)
		print "**** Published " + msg + " to Lights ****"
	elif appliance_id[0] == 'A':
		# the message that should be sent is "AO" or "AF" to turn on all the ACs
		# the message to turn on the particular AC is "1F" i. AC number and the command (O for ON and F for Off)
		msg = 'A ' + str(command)
		client.publish(MQTT_TOPIC_AC, msg, 1)
		print "**** Published " + msg + " to ACs ****"

def mqtt_init():
	print "Inside MQTT Init"
	client.on_connect = on_connect
	client.on_message = on_message

	client.connect(MQTT_HOST, MQTT_PORT, 60)

	client.loop_forever()
