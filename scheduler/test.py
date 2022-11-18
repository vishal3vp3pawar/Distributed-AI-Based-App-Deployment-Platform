import os
import subprocess

fpath=os.getcwd()
app_path="../app_service/Application_repository/"
app_path=app_path+"app1"
aname="app1"
os.chdir(app_path)
command_ = "docker build -t "+aname+" ."
subprocess.Popen(command_,shell=True)
