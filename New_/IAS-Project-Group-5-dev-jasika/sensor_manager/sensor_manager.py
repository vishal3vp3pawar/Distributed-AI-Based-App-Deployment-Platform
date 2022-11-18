import sensor_db
import kafka_manager
import threading
import json

################################ REGISTRATION OF SENSORS INTO MONGODB ##############################


def registerSensorType(sensor_type):
    sensor_db.register_sensor_type(sensor_type)


def registerSensorInstance(sensor_instance):
    topic_name = sensor_db.register_sensor_instance(sensor_instance)

    # Start producing data for the newly added sensor
    kafka_manager.create_kafka_topic(topic_name)
    threading.Thread(target=kafka_manager.produce_data,
                     args=(topic_name,)).start()


def register_sensors_from_json(path):
    f = open(path)
    sensors = json.load(f)
    for instance in sensors['sensor_instances']:
        registerSensorInstance(instance)


############################### RETRIEVING SENSOR DATA FROM KAFKA ###################################

def getSensorData(topic_name):
    return kafka_manager.consume_data(topic_name)


############################### RETRIEVING SENSOR DETAILS USING LOCATION ##############################

def getSensorTypes(sensor_location):
    return sensor_db.get_sensor_types(sensor_location)


def getSensorInstances(sensor_type, sensor_location):
    return sensor_db.get_sensor_instances(sensor_type, sensor_location)


############################## RETRIEVING ALL SENSOR DETAILS ############################################

def getAllSensorTypes():
    return sensor_db.get_all_sensor_types()


def getAllSensorInstances():
    return sensor_db.get_all_sensor_instances()
