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
import download_from_azure
import shutil
import socket
import requests

app = Flask(__name__)


@app.route('/', methods=['POST'])
def pr():
    logging.warning("Hello World")


@app.route('/getLoad', methods=['POST', 'GET'])
def getLoad():
    stream = os.popen('echo $(date +%s%N)')
    tstart = int(stream.read())
    stream = os.popen('echo $(cat /sys/fs/cgroup/cpuacct/cpuacct.usage)')
    cstart = int(stream.read())
    time.sleep(2)
    stream = os.popen('echo $(date +%s%N)')
    tstop = int(stream.read())
    stream = os.popen('echo $(cat /sys/fs/cgroup/cpuacct/cpuacct.usage)')
    cstop = int(stream.read())
    cu = (cstop-cstart)/(tstop-tstart)
    stream = os.popen(
        'echo $(cat /sys/fs/cgroup/memory/memory.usage_in_bytes)')
    mu = int(stream.read())/1024/1024
    mp = mu/200
    return jsonify(cpu_load=cu, mem_load=mu)


def download_model(model_name):

    logging.warning("\n\nIN donwload MODEL\n\n")

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

    path_to_check = desti_dir + "/" + source_name
    if os.path.exists(path_to_check):
        logging.debug("Dir/File already exixsts < DELETING IT NOW >")
        shutil.rmtree(desti_dir + "/" + source_name)
        # logging.debug("Dir/File deleted")

    download_from_azure.download_source(
        source_name,
        source_dir,
        desti_dir,
        connection_string,
        share_name, space=" "
    )


def download_app(app_name):

    share_name = "ias-storage"
    connection_string = "DefaultEndpointsProtocol=https;AccountName=iasproject;AccountKey=QmnE09E9Cl6ywPk8J31StPn5rKPy+GnRNtx3M5VC5YZCxAcv8SeoUHD2o1w6nI1cDXgpPxwx1D9Q18bGcgiosQ==;EndpointSuffix=core.windows.net"

    # pre work
    if os.path.exists("application_repo"):
        # if os.path.exists(f"application_repo/"):
        #     pass
        # else:
        #     os.mkdir(f"application_repo/")
        pass
    else:
        os.mkdir("application_repo")
        # os.mkdir(f"application_repo/")

    source_name = app_name
    source_dir = "application_repo"
    desti_dir = "application_repo"

    path_to_check = desti_dir + "/" + source_name
    if os.path.exists(path_to_check):
        logging.debug("Dir/File already exixsts < DELETING IT NOW >")
        shutil.rmtree(desti_dir + "/" + source_name)
        # logging.debug("Dir/File deleted")

    download_from_azure.download_source(
        source_name,
        source_dir,
        desti_dir,
        connection_string,
        share_name, space=" "
    )


# def get_free_port():
#     while True:
#         rand_port = random.randint(40000, 50000)

#         a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#         location = ("127.0.0.1", rand_port)
#         result_of_check = a_socket.connect_ex(location)

#         try:
#             if result_of_check == 0:
#                 logging.warning(f"Port is open {rand_port}")
#                 a_socket.close()

#                 return rand_port
#             else:
#                 logging.warning(f"Port is not open : {rand_port}")
#                 a_socket.close()
#         except:
#             pass


@app.route('/runapp', methods=['POST', 'GET'])
def runApp():
    logging.warning("got request /runapp from deployer")
    received_json = request.get_json()

    if received_json['schedule_type'] == 1:
        # for MODEL scheduling
        logging.warning(
            f"Model Schedule request with received_json = {received_json}")

        fpath = received_json['fpath']
        model_name = received_json['model_name']

        path = f"model_repo/{model_name}"
        if os.path.exists(path):
            logging.warning("exists")
            logging.warning("exists")
            shutil.rmtree(path)

        #####
        # download repo from azure
        download_model(model_name)
        #####
        logging.warning(os.getcwd())
        logging.warning("\n\n\DOWNLOAD MODEL DONE\n\n\n")
        # print(os.getcwd)
        # docker build image
        # unpickle donwloaded model
        di = 'model_repo/'+model_name
        os.chdir(di)
        logging.warning(os.getcwd())
        command = f"docker build -t {model_name} ."
        # os.system()
        out = subprocess.check_output(command, shell=True)
        out = out.decode('utf-8')
        out = out.strip()

        logging.warning(f"output of build ommand = {out}")

        command = f"docker run -d --rm -it -v /etc/localtime:/etc/localtime:ro --net=host  --name {model_name} {model_name}"

        out = subprocess.check_output(command, shell=True)
        out = out.decode('utf-8')
        out = out.strip()
        logging.warning(f"output of run ommand = {out}")

        return jsonify(container_id=out)
    else:
        # for APP scheduling
        fpath = received_json['fpath']
        app_name = received_json['app_name']
        config = received_json['config']
        port_num = received_json['port_num']

        logging.warning(f"in node config = {config}")
        logging.warning(f"portnumber = {port_num}")

        # remove if already existed
        path = f"application_repo/{app_name}"
        if os.path.exists(path):
            logging.warning("exists")
            logging.warning("exists")
            shutil.rmtree(path)

        #####
        # download repo from azure
        download_app(app_name)
        #####
        logging.warning("\n\n\DOWNLOAD DONE\n\n\n")

        with open(f'./application_repo/{app_name}/{app_name}.json', 'w') as convert_file:
            convert_file.write(json.dumps(config))

        logging.warning("\n\n\DUMP JSON DONE\n\n\n")
        logging.warning(f"os.path.realpath(fpath) = {os.path.realpath(fpath)}")
        os.chdir(os.path.realpath(fpath))
        generate_requirements(app_name)
        generate_docker_file_for_app(app_name)
        logging.warning("\n\n\CHDIR DONE\n\n\n")
        logging.warning(f"app_name = {app_name}")
        logging.warning(f"\n\nos.getcwd() = {os.getcwd()}\n\n")
        logging.warning(f"\n\nos.system('ls') = {os.system('ls')}\n\n")

        ################

        command = f"docker build -t {app_name} ."
        # os.system()
        # out = subprocess.check_output(command, shell=True)
        os.system(command)
        # out = out.decode('utf-8')
        # out = out.strip()

        # logging.warning(f"output of build ommand = {out}")

        command = f"docker run -d --rm -it -p {port_num}:5000 -v /etc/localtime:/etc/localtime:ro --net=host  --name {app_name} {app_name}"
        # os.system(command)
        out = subprocess.check_output(command, shell=True)
        out = out.decode('utf-8')
        out = out.strip()
        logging.warning(f"output of run ommand = {out}")


        pub_ip = requests.get("http://api.ipify.org").content.decode()
        localhost_ip_address = pub_ip
        # localhost_ip_address = "localhost"

        return jsonify(container_id=out, port=port_num, ip=localhost_ip_address)
        ################

        # os.chmod("app.py", 0o0777)
        # logging.warning("\n\n\CHMOD DONE\n\n\n")
        # pat = "./app.py"
        # logging.warning(f"os.path.realpath(pat) = {os.path.realpath(pat)}")
        # logging.warning(f"os.getcwd() = {os.getcwd()}")
        # process = subprocess.Popen(["python", pat], shell=False)
        # return jsonify(pID=process.pid)


def generate_docker_file_for_app(app_name):
    # app_path = f"./application_repo/{app_name}"
    app_path = "."
    # app_id = sys.argv[1]
    # algorithm_number = sys.argv[3]

    docker_file_path = app_path + '/' + "Dockerfile"
    logging.warning(f"docker_file_path = {docker_file_path}")
    logging.warning(f"app_path = {app_path}")
    logging.warning("docker_file_path : {docker_file_path}")
    with open(docker_file_path, "w") as filo:
        filo.write("FROM python:3\n")
        filo.write(f"WORKDIR /{app_name}\n")
        filo.write("COPY requirements.txt requirements.txt\n")
        filo.write("COPY . .\n")

        filo.write(
            "RUN pip3 install -r requirements.txt\n"
            )

        # print("File_name :",onlyfiles)

        filo.write(f'CMD ["python3", "-u","app.py"]')


def generate_requirements(app_name):
    app_path = f"./application_repo/{app_name}"
    # app_id = sys.argv[1]
    # algorithm_number = sys.argv[3]

    req_path = app_path
    logging.warning(req_path)
    logging.warning(app_path)
    logging.warning(f"requirements_file_path : {req_path}")
    logging.warning(f"os.getcwd() = {os.getcwd()}")
    # os.chdir(req_path)
    logging.warning(f"os.getcwd() = {os.getcwd()}")
    os.system('pipreqs .')


@app.route('/killapp', methods=['POST'])
def killApp():
    tmp = request.get_json()
    container_id = tmp['container_id']
    command="docker rm -f " + container_id
    os.system(command)
    # status = os.kill(pid, signal.SIGKILL)
    # out = out.decode('utf-8')
    # out = out.strip()
    # logging.warning(f"KIll app op = {out}")
    return "Killed Successfully"


if __name__ == "__main__":
    # download_app("ac_app")

    # generate_server_file(random.randint(40000, 50000), "ac_app")
    # generate_requirements()
    # generate_docker_file_for_model("ac_prediction_model")

    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=1200)
