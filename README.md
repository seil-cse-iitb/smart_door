Steps to deploy smart_door:
1. git clone the repo in rpi, and a server machine
2. In server machine, cd into flask_server and start services using docker-compose.
3. MQTT_IP & MQTT_PORT need to be configured in docker-compose.yaml in flask_server folder.
4. If MQTT is not available start MQTT in server machine by uncommenting the eclipse-mosquito service in docker-compose.yaml

------smart_door server is running now--------

5. in rpi, change the server url in smart_door.py (variable server_root)
6. run python3 smart_door.py to start smart_door
7. if some error comes, check the other parameters in smart_door.py (master file for smart_door)

------that's it folks------
