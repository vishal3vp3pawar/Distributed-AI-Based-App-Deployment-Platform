# import json
# import mysql.connector
# import uuid
# from kafka import KafkaProducer


# def read_db_configuration(filepath):
#     logging.warning("in read_db_configureation")
#     logging.warning(filepath)
#     f = open(filepath, "r")

#     # Reading from file
#     data = json.loads(f.read())
#     logging.warning(data)
#     host_name = data["host"]
#     user_name = data["user"]
#     password = data["password"]
#     database_name = data["database"]
#     return host_name, user_name, password, database_name


# def insert_data_to_table(tablename, table_column_names, row_data):
#     logging.warning(f"in insert data {tablename}")
#     filepathdb = "configurations/db_config.json"
#     host_name, user_name, password, database_name = read_db_configuration(
#         filepathdb)
    
#     logging.warning(host_name, user_name, password, database_name)
#     mydb = mysql.connector.connect(
#         host=host_name,
#         user=user_name,
#         password=password,
#         database=database_name
#     )

#     logging.warning("connection successful")
#     mycursor = mydb.cursor()

#     table_column_str = ", ".join(i for i in table_column_names)
#     sql = "INSERT INTO "+tablename + \
#         " ("+ table_column_str +") VALUES ("+str(row_data)[1:-1]+")"

#     mycursor.execute(sql)

#     mydb.commit()



# def read_kafka_configuration(filepath):
#     logging.warning("in read_kafka_configuration")
#     logging.warning(filepath)
#     f = open(filepath, "r")

#     # Reading from file
#     data = json.loads(f.read())
#     logging.warning(data)
#     ip = data["ip"]
#     port = data["port"]
#     return ip, port

# def create_topic(topic_name):
#     kafka_config_path = "configurations/kafka_config.json"
#     kafka_ip, kafka_port = read_kafka_configuration()
    
#     producer = KafkaProducer(
#         bootstrap_servers=['{}:{}'.format(kafka_ip,kafka_port)],
#         api_version=(0,10,1)
#     )
    



def sensor_instance_validator(filepath):



    with open(filepath, "r") as read_content:
        logging.warning("FILE CONTENT in validator for SENSOR INSTANCE")
        # logging.warning(json.load(read_content))

        file_content = json.load(read_content)
        logging.warning(file_content)

        uuidstr = str(uuid.uuid4())

        file_new_name = "sensor_instance_" + uuidstr + ".json"

        sensor_instance_id = "sensor_instance_" + uuidstr
        sensor_type = file_content['sensor_type']
        sensor_location = file_content['sensor_location']
        ip = file_content['ip']
        port = file_content['port']

        insert_data_to_table('sensor_instances', 
            ['sensor_instance_id', 'sensor_type', 'ip', 'port', 'location'],
            [sensor_instance_id, sensor_type, ip, port, sensor_location]
        )

        return True