from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import sensor_manager
import sensor_db
import kafka_manager
import json
import pymongo
import logging

client = "mongodb://ias_mongo_user:ias_password@cluster0-shard-00-00.doy4v.mongodb.net:27017,cluster0-shard-00-01.doy4v.mongodb.net:27017,cluster0-shard-00-02.doy4v.mongodb.net:27017/ias_database?ssl=true&replicaSet=atlas-ybcxil-shard-0&authSource=admin&retryWrites=true&w=majority"
db_name = "ias_database"
client = pymongo.MongoClient(client)
mydb = client[db_name]
services_config_coll = mydb["services_config"]


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


################################## SENSOR REGISTRATION ########################################

# @app.route("/registerSensorType", methods=["POST"])
# def registerSensorType():
#     sensor_type = request.json
#     sensor_manager.registerSensorType(sensor_type)
#     return json.dumps({"data": "Registered Sensor Type successfully"})


@app.route("/registerSensorInstance", methods=["POST"])
def registerSensorInstance():
    sensor_instance = request.json
    sensor_manager.registerSensorInstance(sensor_instance)
    return json.dumps({"data": "Registered Sensor Instance successfully"})

################################# GET A SENSOR DATA ###########################################

@app.route("/getSensorData", methods=["POST"])
def getSensorData():
    topic_name = request.json['topic_name']
    sensor_data = sensor_manager.getSensorData(topic_name)
    jsonObj = {
        "sensor_data": sensor_data
    }
    return json.dumps(jsonObj)


################################ GET SENSOR DETAILS USING LOCATION #############################

@app.route("/getSensorTypes", methods=["POST"])
def getSensorTypes():
    sensor_location = request.json['sensor_location']
    sensor_types = sensor_manager.getSensorTypes(sensor_location)
    jsonObj = {
        "sensor_types": sensor_types
    }
    return json.dumps(jsonObj)


@app.route("/getSensorInstances", methods=["POST"])
def getSensorInstances():
    sensor_type = request.json['sensor_type']
    sensor_location = request.json['sensor_location']
    sensor_instances = sensor_manager.getSensorInstances(sensor_type, sensor_location)
    jsonObj = {
        "sensor_instances": sensor_instances
    }
    return json.dumps(jsonObj)


############################### GET ALL SENSOR DETAILS #############################################

@app.route("/getAllSensorTypes", methods=["GET", "POST"])
def getAllSensorTypes():
    sensor_types = sensor_manager.getAllSensorTypes()
    jsonObj = {
        "sensor_types": sensor_types
    }
    return json.dumps(jsonObj)

@app.route("/getAllSensorInstances", methods=["GET", "POST"])
def getAllSensorInstances():
    sensor_instances = sensor_manager.getAllSensorInstances()
    jsonObj = {
        "sensor_instances": sensor_instances
    }
    return json.dumps(jsonObj)


################################### MAIN #############################################################

if __name__ == "__main__":
    if sensor_db.databaseExists() == False:
        logging.warning("Sensor Collection CREATED...")
        sensor_manager.register_sensors_from_json("sensor_config.json")
    else:
        logging.warning("DATABASE ALREADY EXISTS...")
        kafka_manager.produce_sensors_data()
    


    service_ports = services_config_coll.find()

    sensor_service_port = service_ports[0]['sensor_service']



    app.run(debug=True, host='0.0.0.0', port=sensor_service_port)

