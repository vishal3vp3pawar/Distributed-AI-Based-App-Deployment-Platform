import logging
from flask import Flask, request, jsonify
import os
import subprocess
import time
from time import sleep
from subprocess import call
import signal
import json
import download_from_azure
import shutil

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

    # Api Download
    # download_api()



@app.route('/runapp', methods=['POST', 'GET'])
def runApp():
    logging.warning("got request /runapp from deployer")
    received_json = request.get_json()
    fpath = received_json['fpath']
    app_name = received_json['app_name']
    config = received_json['config']

    logging.warning(f"in node config = {config}")


    # remove if already existed
    path = f"application_repo/{app_name}"
    if os.path.exists(path):
        logging.warning("exists")
        logging.warning("exists")
        logging.warning("exists")
        logging.warning("exists")
        logging.warning("exists")
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
    logging.warning("\n\n\CHDIR DONE\n\n\n")
    logging.warning(f"app_name = {app_name}")
    logging.warning(f"os.getcwd() = {os.getcwd()}")
    os.chmod("app.py", 0o0777)
    logging.warning("\n\n\CHMOD DONE\n\n\n")
    pat = "./app.py"
    logging.warning(f"os.path.realpath(pat) = {os.path.realpath(pat)}")
    logging.warning(f"os.getcwd() = {os.getcwd()}")
    process = subprocess.Popen(["python", pat], shell=False)
    return jsonify(pID=process.pid)


@app.route('/killapp', methods=['POST'])
def killApp():
    tmp = request.get_json()
    pid = tmp['proID']
    status = os.kill(pid, signal.SIGKILL)
    return "Killed Successfully"


if __name__ == "__main__":
    # download_app("ac_app")
    app.run(debug=True,use_reloader=False, host="0.0.0.0", port=1200)
