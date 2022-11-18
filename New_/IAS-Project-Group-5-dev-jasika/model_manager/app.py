import logging
from flask import Flask, jsonify, request, render_template, session
from flask import Flask, request, redirect, url_for, flash, render_template
import os
from werkzeug.utils import secure_filename
from zipfile import ZipFile
import json
import pickle
import numpy as np
import download_from_azure
import shutil
from azurerepo2 import create_directory, upload_local_file

from azure.core.exceptions import (
    ResourceExistsError,
    ResourceNotFoundError
)

from azure.storage.fileshare import (
    ShareServiceClient,
    ShareClient,
    ShareDirectoryClient,
    ShareFileClient
)

import pymongo
from flask_pymongo import PyMongo

client = "mongodb://ias_mongo_user:ias_password@cluster0-shard-00-00.doy4v.mongodb.net:27017,cluster0-shard-00-01.doy4v.mongodb.net:27017,cluster0-shard-00-02.doy4v.mongodb.net:27017/ias_database?ssl=true&replicaSet=atlas-ybcxil-shard-0&authSource=admin&retryWrites=true&w=majority"
db_name = "ias_database"
client = pymongo.MongoClient(client)
mydb = client[db_name]
services_config_coll = mydb["services_config"]


share_name = "ias-storage"
connection_string = "DefaultEndpointsProtocol=https;AccountName=iasproject;AccountKey=QmnE09E9Cl6ywPk8J31StPn5rKPy+GnRNtx3M5VC5YZCxAcv8SeoUHD2o1w6nI1cDXgpPxwx1D9Q18bGcgiosQ==;EndpointSuffix=core.windows.net"

# Create a ShareServiceClient from a connection string
service_client = ShareServiceClient.from_connection_string(connection_string)

app = Flask(__name__)
app.config['MONGO_URI'] = "mongodb://ias_mongo_user:ias_password@cluster0-shard-00-00.doy4v.mongodb.net:27017,cluster0-shard-00-01.doy4v.mongodb.net:27017,cluster0-shard-00-02.doy4v.mongodb.net:27017/ias_database?ssl=true&replicaSet=atlas-ybcxil-shard-0&authSource=admin&retryWrites=true&w=majority"
app.config['SECRET_KEY'] = "SuperSecretKey"

mongo_db = PyMongo(app)
db = mongo_db.db

ALLOWED_EXTENSIONS = set(['zip'])


###########################################
###########################################
###########################################
###########################################
###########################################

def download_azure_file(connection_string, share_name, dir_name, file_name):
    try:

        source_file_path = dir_name + "/" + file_name

        file_client = ShareFileClient.from_connection_string(
            connection_string, share_name, source_file_path)
        logging.warning(source_file_path)
        stream = file_client.download_file()
        return stream.readall()

    except ResourceNotFoundError as ex:
        logging.warning("ResourceNotFoundError:", ex.message)


@app.route('/')
def home_page():
    return "<h1>Model Service home page</h1>"


@app.route('/model_url', methods=['POST', 'GET'])
def send_URL():
    if request.method == 'GET':
        return "Sending URL for given model type..."
    json_data = request.get_json()
    model_type = json_data['model_type']
    return "http://demo_url"


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_Zip(zipObj):
    countjson = 0
    countpy = 0
    listOfiles = zipObj.namelist()
    for elem in listOfiles:
        if elem.endswith('.json'):
            countjson += 1
        if elem.endswith('.pkl'):
            countpy += 1
    if (countjson != 1 or countpy != 1):
        return 0
    return 1


def uploadConfig(file_path):
    model_file_name = ''
    with ZipFile(file_path, 'r') as zipObj:
        listOfiles = zipObj.namelist()
        for elem in listOfiles:
            if elem.endswith('.json'):
                if elem.endswith('model_config.json'):
                    model_file_name = elem

    if model_file_name != '':
        zip_obj = ZipFile(file_path, 'r')
        model_json_obj = zip_obj.open(model_file_name)
        json_data = json.load(model_json_obj)
        json_data['_id'] = json_data['model_name']
        logging.warning(json_data)
        try:
            db.model.insert_one(json_data)
        except:
            os.remove(file_path)

    return


"""
@app.route('/upload_model', methods=['POST', 'GET'])
def uploadModel():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # Provided file path
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            share_client = ShareClient.from_connection_string(
                connection_string, share_name)
            flag = True
            for item in list(share_client.list_directories_and_files('model_repo')):
                logging.warning(item['name'])
                if item["is_directory"]:
                    logging.warning(f"Directory: {item['name']}")
                    if item["name"] == filename.split('.')[0]:
                        flag = False
            if flag:
                zipfile = ZipFile(file._file)
                if validate_Zip(zipfile):
                    create_directory(connection_string, share_name,
                                     'model_repo/' + filename.split('.')[0])
                    logging.warning(zipfile.namelist())
                    fileslist = zipfile.namelist()[1:]
                    for name in fileslist:
                        logging.warning(name)
                        newfile = zipfile.read(name)
                        logging.warning('application_repo/' + name)
                        upload_local_file(
                            connection_string, newfile, share_name, 'model_repo/' + name)
                        if name.split('/')[1] == "model_config.json":
                            json_data = json.loads(newfile.decode('utf-8'))
                            logging.warning(json_data)
                            json_data['_id'] = json_data['model_name']
                            db.model.insert_one(json_data)
                else:
                    return "Improper Zip format"
            else:
                return "Model with similar name already exists."
            return redirect(url_for('uploadModel'))

        return render_template('index.html')

    return render_template('index.html')
"""

def download_model_directory(model_name):
    share_name = "ias-storage"
    connection_string = "DefaultEndpointsProtocol=https;AccountName=iasproject;AccountKey=QmnE09E9Cl6ywPk8J31StPn5rKPy+GnRNtx3M5VC5YZCxAcv8SeoUHD2o1w6nI1cDXgpPxwx1D9Q18bGcgiosQ==;EndpointSuffix=core.windows.net"

    # pre work
    if os.path.exists("model_repo"):
        # if os.path.exists(f"application_repo/"):
        #     pass
        # else:
        #     os.mkdir(f"application_repo/")
        pass
    else:
        os.mkdir("model_repo")
        # os.mkdir(f"application_repo/")

    source_name = model_name
    source_dir = "model_repo"
    desti_dir = "model_repo"

    if os.path.exists(desti_dir + "/" + source_name):
        logging.warning("No need to download.... Dir/File already exixsts")
        return

    download_from_azure.download_source(
        source_name,
        source_dir,
        desti_dir,
        connection_string,
        share_name, space="   "
    )



@app.route('/predict', methods=['POST'])
def predictOutput():
    json_data = request.get_json()
    model_name = json_data['model_name']
    ip_data = json_data['data']
    ip_data = np.array(ip_data)

    # model_name = "ac_prediction_model"

    logging.warning(f"MODEL NAME = {model_name}")
    logging.warning(f"MODEL NAME = {model_name}")
    logging.warning(f"MODEL NAME = {model_name}")
    logging.warning(f"MODEL NAME = {model_name}")
    logging.warning(f"MODEL NAME = {model_name}")
    logging.warning(f"MODEL NAME = {model_name}")
    logging.warning(f"MODEL NAME = {model_name}")

    shutil.rmtree("./model_repo")

    download_model_directory(model_name)

    pickle_file = f"model_repo/{model_name}/{model_name}.pkl"
    model_config_file = f"model_repo/{model_name}/model_config.json"
    logging.warning(pickle_file)
    pf=open(pickle_file,"rb")
    AI_model = pickle.load(pf)

    # Prediction
    logging.warning("ip_data:", ip_data)
    prediction_data = AI_model.predict(ip_data)
    prediction_data = prediction_data.tolist()
    logging.warning("pred data:", prediction_data)
    # Response
    jsonObj = {
        "predicted_value": prediction_data
    }
    logging.warning(type(prediction_data))
    logging.warning(prediction_data)

    return json.dumps(jsonObj)


if __name__ == '__main__':

    # predictOutput()

    service_ports = services_config_coll.find()

    model_service_port = service_ports[0]['model_service']

    app.run(debug=True, host='0.0.0.0', port=model_service_port)
