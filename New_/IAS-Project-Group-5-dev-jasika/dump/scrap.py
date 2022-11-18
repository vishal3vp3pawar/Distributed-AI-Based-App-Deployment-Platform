from itsdangerous import json
import numpy as np
import requests

# import random

# x = []
# y = []
# for i in range(0, 1000):
#     x.append(random.randint(0, 30))
#     y.append(random.randint(0, 1))

# f=open("train.csv",'w')
# for i in range(len(x)):
#     f.write("{},{}\n".format(x[i], y[i]))

# f.close()

data = 1
data = np.reshape(np.array(data),(-1, 1))
# logging.warning(data)
# jsonObj= {
#     "data": data
# }
response = requests.post("http://localhost:5003/predict", json={
    "data": data.tolist(),
    "model_name": "ac_prediction_model"
}).content
# logging.warning(jsonObj)
