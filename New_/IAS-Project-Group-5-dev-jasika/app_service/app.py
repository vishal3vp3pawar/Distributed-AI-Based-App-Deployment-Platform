import logging
from asyncio import subprocess
from flask import Flask, request, url_for, render_template, jsonify, session, flash, redirect
from flask_pymongo import PyMongo
from io import BytesIO
from werkzeug.utils import secure_filename
from zipfile import ZipFile
import requests
import json
import os

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
import pymongo, shutil

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

@app.route('/')
def print_val():
    return "hello"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_Zip_app_service(zipObj):
    countjson = 0
    countpy = 0
    listOfiles = zipObj.namelist()
    for elem in listOfiles:
        if elem.endswith('.json'):
            countjson += 1
        if elem.endswith('.py'):
            countpy += 1
    if (countjson != 1 or countpy != 1):
        return 0
    return 1


@app.route('/upload', methods=['GET', 'POST'])
def upload_application():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        


        file = request.files['file']


        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            share_client = ShareClient.from_connection_string(connection_string, share_name)
            flag = True
            for item in list(share_client.list_directories_and_files('application_repo')):
                logging.warning(item['name'])
                if item["is_directory"]:
                    logging.warning(f"Directory: {item['name']}")
                    if item["name"] == filename.split('.')[0]:
                        flag = False
            if flag:

                name = "./temp/" + file.filename
                file.save(name)
                with ZipFile(name, 'a') as zipf:
                    source_path = "./api.py"
                    dest = "api.py"

                    zipf.write(source_path, dest)
                
                zipfile = ZipFile(file._file)
                if validate_Zip_app_service(zipfile):
                    create_directory(connection_string, share_name, 'application_repo/' + filename.split('.')[0])
                    logging.warning(zipfile.namelist())
                    fileslist = zipfile.namelist()[1:]
                    for name in fileslist:
                        logging.warning(name)
                        newfile = zipfile.read(name)
                        logging.warning('application_repo/' + name)
                        upload_local_file(connection_string, newfile, share_name, 'application_repo/' + name)
                        #logging.warning(name.split)
                        if name.split('/')[1] == "application.json": 
                            json_data = json.loads(newfile.decode('utf-8'))
                            logging.warning(json_data)
                            json_data['_id'] = json_data['app_name']
                            db.application.insert_one(json_data)
                else:
                    return "Improper Zip format"
            else:
                return "Application with similar name already exists."
            return redirect(url_for('upload_application'))

    return render_template('index.html')


if __name__ == '__main__':


    service_ports = services_config_coll.find()

    app_service_port = service_ports[0]['app_service']

    app.run(debug=True, host='0.0.0.0', port=app_service_port)
