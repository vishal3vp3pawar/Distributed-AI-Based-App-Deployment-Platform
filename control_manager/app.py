from urllib import response
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from itsdangerous import json
import control_db
import control_manager
import requests
import pymongo

client = "mongodb://ias_mongo_user:ias_password@cluster0-shard-00-00.doy4v.mongodb.net:27017,cluster0-shard-00-01.doy4v.mongodb.net:27017,cluster0-shard-00-02.doy4v.mongodb.net:27017/ias_database?ssl=true&replicaSet=atlas-ybcxil-shard-0&authSource=admin&retryWrites=true&w=majority"
db_name = "ias_database"
client = pymongo.MongoClient(client)
mydb = client[db_name]
services_config_coll = mydb["services_config"]


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


################################## SENSOR REGISTRATION ########################################

@app.route("/performAction", methods=["GET", "POST"])
def performAction():
    instance = request.json
    url = "http://" + instance["sensor_ip"] + ":" + str(instance["sensor_port"]) +"/"
    if instance["sensor_type"] == "fan":
        url += "fanAction"
    elif instance["sensor_type"] == "ac":
        url += "acAction"
    response = requests.post(url, json={
        "data": instance["data"]
    }).content
    return response.decode()

@app.route("/getControlInstances", methods=["POST"])
def getControlInstances():
    sensor_type = request.json['sensor_type']
    sensor_location = request.json['sensor_location']
    control_instances = control_manager.get_control_instances(sensor_type, sensor_location)
    jsonObj = {
        "control_instances": control_instances
    }
    return json.dumps(jsonObj)

################################### MAIN #############################################################

if __name__ == "__main__":
    if control_db.databaseExists() == False:
        logging.warning("Collection CREATED...")
        control_manager.register_controllers_from_json("control_config.json")
    
    
    
    service_ports = services_config_coll.find()

    controller_service_port = service_ports[0]['controller_service']



    app.run(debug=True, host='0.0.0.0', port=controller_service_port)
