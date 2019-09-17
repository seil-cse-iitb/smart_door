#source /home/shinjan/virtualenv/smart-door-v3-backend/bin/activate
#nohup mosquitto -c /home/shinjan/Programs/mqtt/mosquitto.conf &
export FLASK_APP=/home/smart_door/flask_server/server.py
export FLASK_DEBUG=1
cd /home/smart_door/flask_server/
flask run --host=0.0.0.0
