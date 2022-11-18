from fileinput import filename
import subprocess
filename = "ac_app.json"
directory = "ac_app"
cpy_cmd = "cp data/"+directory+"/" + filename + \
    " ../app_service/Application_repository/"+directory+"/"+filename
subprocess.Popen(cpy_cmd, shell=True)
