# Execute this script from inside flask_server directory only
#source /home/shinjan/virtualenv/smart-door-v3-backend/bin/activate
#nohup mosquitto -c /home/shinjan/Programs/mqtt/mosquitto.conf &
export FLASK_APP=$PWD/server.py
export FLASK_DEBUG=1
flask run --host=0.0.0.0
