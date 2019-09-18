# need to change mqtt ip address in static/js/contoller.js line 73 for front-end to work



# Running
*  nohup mosquitto -c /home/shinjan/Programs/mqtt/mosquitto.conf &
* `export FLASK_APP=~/Workspaces/smart-door-v3/Server/server.py`
* `export FLASK_DEBUG=1`
* `flask run --host=0.0.0.0`
* Always run the last command from inside the project file else csv file cannot be found
