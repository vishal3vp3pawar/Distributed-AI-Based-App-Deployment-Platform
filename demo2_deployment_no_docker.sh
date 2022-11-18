#!/bin/bash

cd ui_manager
gnome-terminal --title="ui_manager" -x bash -c "python3 app.py; exec bash"


cd ../model_manager
gnome-terminal --title="model_manager" -x bash -c "python3 app.py; exec bash"


cd ../app_service
gnome-terminal --title="app_service" -x bash -c "python3 app.py; exec bash"

cd ../scheduler
gnome-terminal --title="scheduler" -x bash -c "python3 app.py; exec bash"

cd ../deployer
gnome-terminal --title="deployer" -x bash -c "python3 app.py; exec bash"


cd ../sensor_manager
gnome-terminal --title="sensor_manager" -x bash -c "python3 app.py; exec bash"

cd ../control_manager
gnome-terminal --title="control_manager" -x bash -c "python3 app.py; exec bash"


cd ../node_manager
gnome-terminal --title="node_manager" -x bash -c "python3 app.py; exec bash"

cd ../node
gnome-terminal --title="node" -x bash -c "python3 app.py; exec bash"


cd ../controllers
gnome-terminal --title="controllers" -x bash -c "python3 ac_server.py 7001; exec bash"
