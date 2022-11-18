import os
import json
from azure.storage.fileshare import ShareDirectoryClient
from azure.storage.fileshare import ShareFileClient
import logging




def helper_download_dir(source_dir, desti_dir, c_str, s_name, space = ""):
    logging.warning(f"in HELPER, {source_dir}, {desti_dir}")
    dir_client = ShareDirectoryClient.from_connection_string(conn_str=c_str, share_name=s_name, directory_path=source_dir)

    my_list = []
    for item in dir_client.list_directories_and_files():
        my_list.append(item)

    for ele in my_list:
        logging.warning(f"{space}, {ele}")

        if ele['is_directory']:
            os.mkdir(desti_dir + "/" + ele['name'])
            helper_download_dir(source_dir + "/" + ele['name'], desti_dir + "/" + ele['name'], c_str, s_name, space + "   ")
        else:

            file_client = ShareFileClient.from_connection_string(conn_str=c_str, share_name=s_name, file_path=source_dir + "/" + ele['name'])

            with open(desti_dir + "/" + ele['name'], "wb") as data:
                stream = file_client.download_file()
                data.write(stream.readall())

def download_source(source_name, source_dir, desti_dir, c_str, s_name, space = ""):

    dir_client = ShareDirectoryClient.from_connection_string(conn_str=c_str, share_name=s_name, directory_path=source_dir)

    flag = True
    sorce_info = None
    
    for ele in dir_client.list_directories_and_files():
        logging.warning(f"ele = {ele}")
        if ele['name'] == source_name:
            logging.warning("NAME MATCHED")
            sorce_info = ele
            flag = False
            break

    if flag:
        logging.warning("source Not Exist")
        return

    logging.warning(sorce_info)

    if sorce_info['is_directory']:
        os.mkdir(desti_dir + "/" + ele['name'])
        helper_download_dir(source_dir + "/" + ele['name'], desti_dir + "/" + ele['name'], c_str, s_name, space + "   ")
    
    else:
        file_client = ShareFileClient.from_connection_string(conn_str=c_str, share_name=s_name, file_path=source_dir + "/" + ele['name'])

        with open(desti_dir + "/" + ele['name'], "wb") as data:
            stream = file_client.download_file()
            data.write(stream.readall())

    logging.warning("Download Complete")


# filepathrepo = "configuration/repo_config.json"
# c_str, s_name = read_json_repo(filepathrepo)

# source_name = "apps_info"
# source_dir = "repository"
# desti_dir = "repository"

# download_source(source_name, source_dir, desti_dir, c_str, s_name, space="   ")
