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
	return str(predictions)

if __name__ == "__main__":
	po=40000
	model=open('ac_prediction_model.pkl','rb')
	model=pickle.load(model)
	app.run(host="0.0.0.0",debug=True,port=40000)