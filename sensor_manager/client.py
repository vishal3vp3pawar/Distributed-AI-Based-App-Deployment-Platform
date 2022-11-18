import logging
from urllib import response
from itsdangerous import json
import requests

def getData(topic_name):
    # localhost_ip_address = "172.17.0.1"
    pub_ip = requests.get("http://api.ipify.org").content.decode()
    # localhost_ip_address = pub_ip
    localhost_ip_address = "localhost"
    
    response = requests.post(
        f"http://{localhost_ip_address}:5000/getSensorData",
        json={
        "topic_name": topic_name
        }
    )
    logging.warning(response.json)

getData()