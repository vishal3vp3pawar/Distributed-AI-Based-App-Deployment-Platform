import logging
import azurerepo2
from zipfile import ZipFile
import os
from flask import Flask, jsonify, render_template, request, flash, redirect, url_for, session
from werkzeug.utils import secure_filename

import requests
import socket
import random
import json
import sensor_type_validator
import sensor_instance_validator

import flask
from flask import Flask, render_template, request, flash, redirect, url_for
#from importlib_metadata import method_cache
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_manager, login_user, logout_user, login_required, UserMixin, current_user

import pymongo
import shutil
import model_util

# from azure.core.exceptions import (
#     ResourceExistsError,
#     ResourceNotFoundError
# )

from azure.storage.fileshare import (
    ShareServiceClient,
    ShareClient,
    ShareDirectoryClient,
    ShareFileClient
)

from azurerepo2 import create_directory, upload_local_file
from flask_pymongo import PyMongo


client = "mongodb://ias_mongo_user:ias_password@cluster0-shard-00-00.doy4v.mongodb.net:27017,cluster0-shard-00-01.doy4v.mongodb.net:27017,cluster0-shard-00-02.doy4v.mongodb.net:27017/ias_database?ssl=true&replicaSet=atlas-ybcxil-shard-0&authSource=admin&retryWrites=true&w=majority"
db_name = "ias_database"
client = pymongo.MongoClient(client)
mydb = client[db_name]
services_config_coll = mydb["services_config"]

share_name = "ias-storage"
connection_string = "DefaultEndpointsProtocol=https;AccountName=iasproject;AccountKey=QmnE09E9Cl6ywPk8J31StPn5rKPy+GnRNtx3M5VC5YZCxAcv8SeoUHD2o1w6nI1cDXgpPxwx1D9Q18bGcgiosQ==;EndpointSuffix=core.windows.net"


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Users.db'
app.config['SECRET_KEY'] = 'secretKey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MONGO_URI'] = "mongodb://ias_mongo_user:ias_password@cluster0-shard-00-00.doy4v.mongodb.net:27017,cluster0-shard-00-01.doy4v.mongodb.net:27017,cluster0-shard-00-02.doy4v.mongodb.net:27017/ias_database?ssl=true&replicaSet=atlas-ybcxil-shard-0&authSource=admin&retryWrites=true&w=majority"

db = SQLAlchemy(app)
mongodb = PyMongo(app)
db1 = mongodb.db
login_manager = LoginManager()
login_manager.init_app(app)




class UserLogin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def get_id(self):
        return self.id

    def is_active(self):
        return self.is_active

    def activate_user(self):
        self.is_active = True

    def get_username(self):
        return self.username

    def get_email(self):
        return self.email


@login_manager.user_loader
def load_user(user_id):
    return UserLogin.query.get(int(user_id))


# APIS

@app.route("/")
def root():
    return render_template('login.html')


# signup
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        logging.warning("in register post")
        username = request.form.get('username')
        # roll = request.form.get('roll')
        email = request.form.get('email')
        password = request.form.get('password')

        logging.warning(username, email, password)

        does_user_exist = UserLogin.query.filter_by(username=username).first()
        if does_user_exist:
            logging.warning("Signup failed")

            return render_template('register.html', error="username exists.")
        else:
            real = UserLogin(username=username, email=email, password=password)
            db.session.add(real)
            db.session.commit()
            data = {
                "_id" : username,
                "username" : username,
                "email" : email
            }
            db1.user.insert_one(data)
        return redirect(url_for('login'))

    return render_template('register.html')


# signup_success


@app.route("/signup_success")
def signup_success():
    pass


@app.route("/login", methods=["GET", "POST"])
def login():
    logging.warning("in login method")
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        logging.warning(f"{username} {password}")

        check_user = UserLogin.query.filter_by(username=username).first()
        logging.warning(f"check_user = {check_user}")
        if(check_user is not None):
            # if current_user.is_authenticated:
            #     resp['msg'] = 'Already logged in.'
            #     resp['role'] = check_user.urole
            #     return redirect()
            logging.warning("checking password")
            if(check_user.password == password):
                login_user(check_user)
                logging.warning("password match")
                # resp['msg'] = 'Logged in successfully'
                # resp['role'] = check_user.urole
                return redirect(url_for('home'))
            else:
                # resp['msg'] = 'Incorrect password'
                # resp['role'] = 'not logged in'
                return render_template('login.html', error=error)
        else:
            # resp['msg'] = "No such User exists"
            # resp['role'] = 'not logged in'
            return render_template('login.html', error=error)

    else:
        return render_template('login.html', error=error)


# logout
@app.route("/logout")
@login_required
def logout():
    logging.warning("in logout")
    logout_user()
    return redirect(url_for('login'))


# home

@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    return render_template('home.html',data = current_user.username)


# sensor_type_upload
@app.route("/sensor_type_upload", methods=["GET", "POST"])
@login_required
def sensor_type_upload():
    if request.method == "POST":
        logging.warning("IN SENSOR TYPE UPLOAD REQUEST")
        uploaded_file = request.files['customFile']
        # uploaded_file = request.form.get('customFile')

        try:
            shutil.rmtree("temp/")
        except Exception:
            pass

        os.mkdir("temp")

        if uploaded_file.filename != '':

            name = "temp/" + uploaded_file.filename
            uploaded_file.save(name)
            with open(name, "r") as read_content:
                logging.warning("FILE CONTENT")
                logging.warning(json.load(read_content))

            validation_result = sensor_type_validator.sensor_type_validator(
                name)
            if(validation_result):
                # I can have a message here too
                return render_template('sensor_type_upload.html', message=("Validation successful"))
            else:
                return render_template('sensor_type_upload.html', error=("Validation Failed"))

        else:
            return render_template('sensor_type_upload.html', error="No file choosen")

    return render_template('sensor_type_upload.html')


@app.route("/sensor_instance_upload", methods=["GET", "POST"])
@login_required
def sensor_instance_upload():
    if request.method == "POST":
        logging.warning("IN SENSOR INSTANCE UPLOAD REQUEST")
        uploaded_file = request.files['customFile']
        # uploaded_file = request.form.get('customFile')

        try:
            shutil.rmtree("temp/")
        except Exception:
            pass

        os.mkdir("temp")

        if uploaded_file.filename != '':

            name = "temp/" + uploaded_file.filename
            uploaded_file.save(name)
            with open(name, "r") as read_content:
                logging.warning("FILE CONTENT")
                logging.warning(json.load(read_content))

            validation_result = sensor_instance_validator.sensor_instance_validator(
                name)
            if(validation_result):
                # I can have a message here too
                return render_template('sensor_instance_upload.html', message=("Validation successful"))
            else:
                return render_template('sensor_instance_upload.html', error=("Validation Failed"))

        else:
            return render_template('sensor_type_upload.html', error="No file choosen")

    return render_template('sensor_instance_upload.html')


# controller_type_upload
@app.route("/controller_type_upload", methods=["GET", "POST"])
@login_required
def controller_type_upload():
    return render_template('controller_type_upload.html')


# controller_instance_upload
@app.route("/controller_instance_upload", methods=["GET", "POST"])
@login_required
def controller_instance_upload():
    return render_template('controller_instance_upload.html')


# model_upload


def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['zip'])

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_Zip_app_service(zipObj):
    countjson = 0
    countpy = 0
    listOfiles = zipObj.namelist()
    for elem in listOfiles:
        if elem.endswith('.json'):
            countjson += 1
        if elem.endswith('.py'):
            countpy += 1
    if (countjson != 1 or countpy != 2):
        return 0
    return 1


def validate_Zip_model_service(zipObj):
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


# def download_azure_file(connection_string, share_name, dir_name, file_name):
#     try:

#         source_file_path = dir_name + "/" + file_name

#         file_client = ShareFileClient.from_connection_string(
#             connection_string, share_name, source_file_path)

#         stream = file_client.download_file()
#         return stream.readall()

#     except ResourceNotFoundError as ex:
#         logging.warning("ResourceNotFoundError:", ex.message)

@login_required
def get_user_details():
    # username = current_user.username
    # email = current_user.email
    # id = current_user.id

    res = {}

    res['username'] = current_user.username
    res['email'] = current_user.email
    res['id'] = current_user.id

    return res



@app.route("/model_upload", methods=["GET", "POST"])
@login_required
def model_upload():
    logging.warning("got request model upload")
    if request.method == 'POST':

        uploaded_file = request.files['customFile']

        logging.warning(uploaded_file.filename)

        if 'customFile' not in request.files:
            logging.warning("'file' not in request.files:")
            flash('No file part')
            return render_template('home.html')
        file = request.files['customFile']
        if file.filename == '':
            logging.warning("no selected file")
            flash('No selected file')
            return render_template('home.html')

        
        
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
                        azurerepo2.delete_dir_tree(connection_string,
                            share_name,
                            "model_repo/"+item["name"]
                        )
                        # flag = False
            
            logging.warning("before validation")

            if flag:
                if os.path.exists("./tmp"):
                    shutil.rmtree("./tmp")
                
                os.mkdir("./tmp")

                port_num = 40000
                model_name = filename.split('.')[0]
                model_util.generate_server_file(port_num, model_name)
                model_util.generate_requirements()
                model_util.generate_docker_file_for_model(model_name)


                name = "./tmp/" + file.filename
                logging.warning(f"type(file) = {type(file)}")
                file.save(name)
                with ZipFile(name, 'a') as zipf:
                    source_path1 = "./tmp/Dockerfile"
                    source_path2 = "./tmp/requirements.txt"
                    source_path3 = "./tmp/server.py"
                    logging.warning(os.getcwd())
                    logging.warning("sending to ")
                    logging.warning(f"{file.filename.split('.')[0]}/api.py")
                    
                    
                    dest1 = f"{file.filename.split('.')[0]}/Dockerfile"
                    dest2 = f"{file.filename.split('.')[0]}/requirements.txt"
                    dest3 = f"{file.filename.split('.')[0]}/server.py"

                    zipf.write(source_path1, dest1)
                    zipf.write(source_path2, dest2)
                    zipf.write(source_path3, dest3)
                
                file.save("./tmp/testing.zip")



                
                zipfile = ZipFile(name)
                

                # zipfile = ZipFile(file._file)
                if validate_Zip_model_service(zipfile):
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
                            json_data['user_details'] = get_user_details()
                            logging.warning(json_data)
                            json_data['_id'] = json_data['model'][0]['model_name']

                            try:
                                db1.model.insert_one(json_data)
                            except:
                                pass
                    

                    # call to scheduler with "model_schedule" request and model_name
                    json_to_send = {}
                    json_to_send['model_name'] = filename.split('.')[0]
                    json_to_send['schedule_type'] = 1
                    json_to_send['user_details'] = get_user_details()
                    json_to_send['port_num'] = port_num

                    # pub_ip = requests.get("http://api.ipify.org/").content.decode()
                    pub_ip = "localhost"
                    
                    service_ports = services_config_coll.find()
                    scheduler_service_port = service_ports[0]['scheduler_service']

                    requests.post(
                        f"http://{pub_ip}:{scheduler_service_port}/schedule_model_request",
                        json=json_to_send
                    )



                            
                else:
                    return "Improper Zip format"
            # else:
            #     return "Model with similar name already exists."
            return render_template('home.html')

    return render_template('model_upload.html')



# app_upload
@app.route("/app_upload", methods=["GET", "POST"])
@login_required
def app_upload():
    logging.warning("in app upload request")
    if request.method == 'POST':
        logging.warning("in post request")
        if 'customFile' not in request.files:
            logging.warning("flash('No file part')")
            flash('No file part')
            return redirect(request.url)

        
        file = request.files['customFile']

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
                        azurerepo2.delete_dir_tree(connection_string,
                            share_name,
                            "application_repo/"+item["name"]
                        )
                        # flag = False
            if flag:

                
                name = "./temp/" + file.filename
                logging.warning(f"type(file) = {type(file)}")
                file.save(name)
                with ZipFile(name, 'a') as zipf:
                    source_path = "./api.py"
                    logging.warning(os.getcwd())
                    logging.warning("sending to ")
                    logging.warning(f"{file.filename.split('.')[0]}/api.py")
                    
                    
                    dest = f"{file.filename.split('.')[0]}/api.py"

                    zipf.write(source_path, dest)
                
                file.save("./temp/testing.zip")



                # zipfile = ZipFile(file._file)
                zipfile = ZipFile(name)
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
                            x = current_user.username
                            json_data['user'] = x

                            try:

                                db1.application.insert_one(json_data)
                            except:
                                pass
                else:
                    return "Improper Zip format"
            # else:
            #     return "Application with similar name already exists."
            return render_template('home.html')

    return render_template('app_upload.html')


# configuration_upload
@app.route("/configuration_upload", methods=["GET", "POST"])
@login_required
def configuration_upload():
    service_ports = services_config_coll.find()

    scheduler_service_port = service_ports[0]['scheduler_service']
    # service_ports[0]['scheduler_service']
    # localhost_ip_address = "172.17.0.1"
    pub_ip = requests.get("http://api.ipify.org").content.decode()
    localhost_ip_address = pub_ip
    # localhost_ip_address = "localhost"
    logging.warning(f"Redirecting to {localhost_ip_address}")
    return redirect(f"http://{localhost_ip_address}:{scheduler_service_port}/")





if __name__ == '__main__':

    service_ports = services_config_coll.find()

    service_name = 'ui_service'

    ui_service_port = service_ports[0]['ui_service']



    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=ui_service_port)
