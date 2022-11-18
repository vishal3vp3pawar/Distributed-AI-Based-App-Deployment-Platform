import api
import numpy as np
from time import sleep


# data_file = open('application.json')
# data = json.load(data_file)
# sd = data['sensor']

while(1):
    data = api.getSensorData()
    data = np.reshape(np.array(data), (-1, 1))
    prediction = api.predict(data)
    output = api.controllerAction(prediction[0])
    logging.warning(output)
    sleep(60)
