from gc import collect
import json
from pydoc_data.topics import topics
from sys import api_version
import pymongo
import threading
from pydoc import doc


client = "mongodb://ias_mongo_user:ias_password@cluster0-shard-00-00.doy4v.mongodb.net:27017,cluster0-shard-00-01.doy4v.mongodb.net:27017,cluster0-shard-00-02.doy4v.mongodb.net:27017/ias_database?ssl=true&replicaSet=atlas-ybcxil-shard-0&authSource=admin&retryWrites=true&w=majority"
db_name = "ias_database"
client = pymongo.MongoClient(client)
mydb = client[db_name]
instancesdb = mydb["ControlInstances"]



# client = pymongo.MongoClient("mongodb://localhost:27017/")
# mydb = client["SensorDatabase"]
# instancesdb = mydb["ControlInstances"]

################################ DATABASE CREATION and DROPPING ################################


def databaseExists():
    databases = client.list_database_names()
    # if 'SensorDatabase' in databases:
    if db_name in databases:
        for collection in mydb.list_collection_names():
            if collection == 'ControlInstances':
                return True
    return False
    # register_sensors_from_json('sensor_config.json')


def drop_db():
    instancesdb.drop()
    # client.drop_database("SensorDatabase")
    client.drop_database(db_name)


def getCount(collectionObj):
    '''Returns no.of documents in the given collection object'''
    return collectionObj.count_documents({})

################################ REGISTRATION OF SENSORS ########################################


def register_control_instance(control_instance):
    '''Stores the given control_instance in the collection'''
    count = getCount(instancesdb)
    control_instance['_id'] = count+1
    instancesdb.insert_one(control_instance)


################################# RETRIEVING DETAILS OF ALL SENSORS ######################

def get_all_control_types():
    control_types = set()
    for document in instancesdb.find():
        control_types.add(document['sensor_type'])
    control_types = list(control_types)
    return control_types


def get_all_control_instances():
    control_instances = []
    for document in instancesdb.find():
        control_instances.append(document)
    return control_instances


def get_ip_and_port(sensor_type, sensor_location):
    for document in instancesdb.find():
        if document['sensor_type'] == sensor_type and document['sensor_location'] == sensor_location:
            return document['sensor_ip'], document['sensor_port']

############################### RETRIEVING BASED ON LOCATION ############################


def get_control_types(sensor_location):
    control_types = set()
    for document in instancesdb.find():
        if document['sensor_location'] == sensor_location:
            control_types.add(document['sensor_type'])
    control_types = list(control_types)
    return control_types


def get_control_instances(sensor_type, sensor_location):
    control_instances = []
    for document in instancesdb.find():
        if document['sensor_type'] == sensor_type and document['sensor_location'] == sensor_location:
            control_instances.append(document)
    return control_instances

#################################################################################################

# drop_db()
# register_sensors_from_json('sensor_config.json')
