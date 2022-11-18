import api
import numpy as np
from time import sleep


# data_file = open('application.json')
# data = json.load(data_file)
# sd = data['sensor']

while(1):
    data = api.getSensorData()
    temperature = data
    data = np.reshape(np.array(data), (-1, 1))
    prediction = api.predict(data)
    output = api.controllerAction(prediction[0])
    print("Temperature is:", temperature, "and action taken:", output)
    sleep(60)
