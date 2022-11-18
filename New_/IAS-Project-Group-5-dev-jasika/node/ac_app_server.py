from flask import Flask,request
import sklearn
import pickle
import pandas as pd
import numpy as np
app=Flask(__name__)
model = None
@app.route('/predict',methods=['POST'])
def predict():
	data = request.get_json()
	predictions = model.predict(data["input"])
	return predictions

if __name__ == "__main__":
	po=47719
	model=open('ac_app.pkl','rb')
	model=pickle.load(model)
	app.run(host="0.0.0.0",debug=True,port=47719)