import sys
import logging
from flask import Flask, request, jsonify
import os
import random
import subprocess
import time
from time import sleep
from subprocess import call
import signal
import json
# import download_from_azure
import shutil
import socket






def generate_docker_file_for_model(app_name):
    app_path = "./tmp"
    # app_id = sys.argv[1]
    # algorithm_number = sys.argv[3]

    docker_file_path = app_path + '/' + "Dockerfile"
    logging.warning(docker_file_path)
    logging.warning(app_path)
    logging.warning("docker_file_path : {docker_file_path}")
    with open(docker_file_path, "w") as f:
        f.write("FROM python:3\n")
        f.write("WORKDIR /tmp\n")
        f.write("COPY requirements.txt requirements.txt\n")

        f.write(
            "RUN pip3 install --no-cache-dir -r requirements.txt\n")
        f.write("COPY . .\n")

        # print("File_name :",onlyfiles)

        f.write(f'CMD ["python3", "-u","server.py"]')


def generate_requirements():
    

    app_path = "./tmp"
    # app_id = sys.argv[1]
    # algorithm_number = sys.argv[3]

    req_file_path = app_path + '/' + "requirements.txt"
    logging.warning(req_file_path)
    logging.warning(app_path)
    logging.warning("req_file_path : {req_file_path}")
    with open(req_file_path, "w") as f:
        f.write("scikit-learn\n")
        f.write("pandas\n")
        f.write("numpy\n")
        f.write("flask\n")
        f.write("requests\n")


# def generate_server_file(port_num, model_name):
#     f = open(f"./tmp/server.py", "w")
#     mname = model_name+".pkl"
#     f.write("from flask import Flask,request\n")
#     f.write('import sklearn\n')
#     f.write('import pickle\n')
#     f.write('import pandas as pd\n')
#     f.write('import numpy as np\n')
#     f.write('app=Flask(__name__)\n')
#     f.write('model = None\n')
#     f.write("@app.route('/predict',methods=['POST'])\n")
#     f.write('def predict():\n')
#     f.write('\tdata = request.get_json()\n')
#     f.write('\tpredictions = model.predict(data["input"])\n')
#     f.write('\treturn predictions\n')
#     f.write('\nif __name__ == "__main__":\n')
#     # f.write('\tdata=request.json\n')
#     # f.write('\tdata=pd.read_json(data)\n')
#     f.write(f'\tpo={port_num}\n')
#     f.write("\tmodel=open('" + model_name + ".pkl','rb')\n")
#     f.write('\tmodel=pickle.load(model)\n')
    
#     f.write(f'\tapp.run(host="0.0.0.0",debug=True,port={port_num})')


# # model_name = sys.argv[1]
# # port_num = sys.argv[2]

# # generate_server_file(port_num, model_name)
# # generate_requirements()
# # generate_docker_file_for_model(model_name)
