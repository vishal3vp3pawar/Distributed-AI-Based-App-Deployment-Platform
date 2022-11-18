import requests
import json
import random
import pymongo

pub_ip = requests.get("http://api.ipify.org").content.decode()
# localhost_ip_address = pub_ip
localhost_ip_address = "localhost"

client = "mongodb://ias_mongo_user:ias_password@cluster0-shard-00-00.doy4v.mongodb.net:27017,cluster0-shard-00-01.doy4v.mongodb.net:27017,cluster0-shard-00-02.doy4v.mongodb.net:27017/ias_database?ssl=true&replicaSet=atlas-ybcxil-shard-0&authSource=admin&retryWrites=true&w=majority"
db_name = "ias_database"
client = pymongo.MongoClient(client)
mydb = client[db_name]
nodes_collection = mydb["nodes_collection"]
services_config_coll = mydb["services_config"]

service_ports = services_config_coll.find()
node_service_port = service_ports[0]['node_service']

sensor_service_port = service_ports[0]['sensor_service']
controller_service_port = service_ports[0]['controller_service']
model_service_port = service_ports[0]['model_service']

sensor_url = f'http://{localhost_ip_address}:{sensor_service_port}/'
control_url = f'http://{localhost_ip_address}:{controller_service_port}/'
model_url = f'http://{localhost_ip_address}:{model_service_port}/'
model_name = "ac_prediction_model"


def readFromFile(path, key):
    f = open(path, 'r')
    data = json.load(f)
    if key == "sensor_details":
        data = data["sensor_details"]
        return data['sensor_type'], data['sensor_location'], data['no_of_instances']
    elif key == "controller_details":
        data = data["controller_details"]
        return data['sensor_type'], data['sensor_location']


def get_public_ip():
    resp = requests.get("http://api.ipify.org/").content.decode()
    # return "172.17.0.1"
    # return "localhost"
    return resp

def getSensorInstances(path="ac_app.json"):
    sensor_type, sensor_location, no_of_instances = readFromFile(
        path, "sensor_details")

    pub_ip = get_public_ip()
    url = f"http://{pub_ip}:{sensor_service_port}/"+'getSensorInstances'
    # logging.warning(url)
    response = requests.post(url=url, json={
        "sensor_type": sensor_type[0],
        "sensor_location": sensor_location
    }).content
    data = json.loads(response.decode())
    sensor_instances = data["sensor_instances"]
    return sensor_instances, no_of_instances


def getControlInstances(path="ac_app.json"):
    sensor_type, sensor_location = readFromFile(path, "controller_details")

    pub_ip = get_public_ip()

    url = f"http://{pub_ip}:{controller_service_port}/"+'getControlInstances'
    # logging.warning(url)
    response = requests.post(url=url, json={
        "sensor_type": sensor_type,
        "sensor_location": sensor_location
    }).content
    data = json.loads(response.decode())
    control_instances = data['control_instances']
    return control_instances


def getSensorData():
    all_instances, no_of_instances = getSensorInstances()
    sensor_instances = random.sample(all_instances, no_of_instances)

    pub_ip = get_public_ip()
    url = f"http://{pub_ip}:{sensor_service_port}/"+'getSensorData'
    # logging.warning(url)
    response = requests.post(url=url, json={
        "topic_name": sensor_instances[0]
    }).content
    data = json.loads(response.decode())
    data = data['sensor_data']
    return data[-1]


def controllerAction(data):
    all_instances = getControlInstances()
    instance = all_instances[0]
    # url = control_url+'performAction'
    pub_ip = get_public_ip()
    url = f"http://{pub_ip}:{controller_service_port}/"+'performAction'
    response = requests.post(url=url, json={
        "sensor_type": instance["sensor_type"],
        "sensor_ip": instance["sensor_ip"],
        "sensor_port": instance["sensor_port"],
        "data": int(data)
    }).content
    return response.decode()


def predict(data):
    # MAKE API call to the model
    # url = model_url+'predict'
    pub_ip = get_public_ip()
    url = f"http://{pub_ip}:{model_service_port}/"+'predict'
    # logging.warning("Data: ", data.tolist())
    # data = data.tolist()
    # logging.warning(type(data))
    response = requests.post(url=url, json={
        "data": data.tolist(),
        "model_name": model_name
    }).content
    prediction = json.loads(response.decode())
    prediction = prediction["predicted_value"]
    return prediction


# getSensorData("light", "himalaya-block")
# readFromFile()
