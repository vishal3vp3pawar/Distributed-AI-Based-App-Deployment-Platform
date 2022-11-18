import logging
from flask_pymongo import PyMongo
from flask import Flask, request, jsonify
import threading
import json
import time
import pymongo
import requests
import sys
import socket

client = "mongodb://ias_mongo_user:ias_password@cluster0-shard-00-00.doy4v.mongodb.net:27017,cluster0-shard-00-01.doy4v.mongodb.net:27017,cluster0-shard-00-02.doy4v.mongodb.net:27017/ias_database?ssl=true&replicaSet=atlas-ybcxil-shard-0&authSource=admin&retryWrites=true&w=majority"
db_name = "ias_database"
client = pymongo.MongoClient(client)
mydb = client[db_name]
nodes_collection = mydb["nodes_collection"]
services_config_coll = mydb["services_config"]

app = Flask(__name__)
app.config['DEBUG'] = True

app.config['MONGO_URI'] = "mongodb://ias_mongo_user:ias_password@cluster0-shard-00-00.doy4v.mongodb.net:27017,cluster0-shard-00-01.doy4v.mongodb.net:27017,cluster0-shard-00-02.doy4v.mongodb.net:27017/ias_database?ssl=true&replicaSet=atlas-ybcxil-shard-0&authSource=admin&retryWrites=true&w=majority"


mongo_db = PyMongo(app)
db = mongo_db.db


#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################

def json_deserializer(data):
    return json.dumps(data).decode('utf-8')


def json_serializer(data):
    return json.dumps(data).encode("utf-8")


@app.route('/getNode', methods=['POST', 'GET'])
def getNode():

    # f=open("node.json")

    # 3
    service_ports = services_config_coll.find()

    node_service_port = service_ports[0]['node_service']

    try:
        data = list(db.nodes_collection.find({}))
        logging.warning(data)
    except:
        pass

    node_list = list()

    for node in data:
        logging.warning(node['ip'])
        logging.warning(node['port'])
        node_ip = node['ip']
        node_port = node['port']
        node_list.append(f"http://{node['ip']}:{node['port']}")
    # 3
    logging.warning(node_list)

    loads = {}
    # data=json.load(f)
    # ni=data["node"]
    # logging.warning(ni)
    for item in node_list:
        rgl = item+"/getLoad"
        req = requests.get(url=rgl).json()
        cl = str(req['cpu_load'])
        cm = str(req['mem_load'])
        tup = (cm, cl)
        loads[item] = tup
    srt = sorted([(value, key) for (key, value) in loads.items()])
    # logging.warning()
    rdf = srt[0]
    ke = list(loads.keys())
    logging.warning(ke[0])
    logging.warning("Deploy on {ke[0]} file=sys.stderr")
    logging.warning(cl+"\t"+cm)
    return ke[0]


if __name__ == "__main__":
    # logging.warning(f"resp = {get_node_for_deployment().decode()}")

    # getNode()

    service_ports = services_config_coll.find()
    node_service_port = service_ports[0]['node_service']
    app.run(debug=True, host='0.0.0.0', port=node_service_port)
