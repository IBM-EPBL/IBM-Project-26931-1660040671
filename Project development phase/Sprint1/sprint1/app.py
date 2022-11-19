import numpy as np
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.inception_v3 import preprocess_input
import requests

from flask import Flask, request, render_template, redirect, url_for

from cloudant.client import Cloudant

client = Cloudant.iam('eaea0c4d-acdc-48ac-a4c5-dacf9847810f-bluemix','nAoFO-_pU1j297US860S3RUPuYvBbqwn6KJvKphIkjZc',connect=True)

my_database = client.create_database('my_database')


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index.html')
def home():
    return render_template('index.html')


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/afterreg', methods=['POST'])
def afterreg():
    x= [x for x in request.form.values() ]
    print(x)
    data = {
        '_id': x[1],
        'name': x[0],
        'psw': x[2]
    }
    print(data)

    query = {'_id': {'Seq': data['_id']}}

    docs = my_database.get_query_result(query)
    print(docs)

    print(len(docs.all()))

    if(len(docs.all())==0):
        url = my_database.create_document(data)
        #response = requests.get(url)
        return render_template('register.html',pred="Registration Successfull, Please login using your details")
    else:
        return render_template('register.html', pred="You are already a member, please login using your details")


@app.route('/login')
def login():
    return ( render_template('login.html'))

@app.route('/afterlogin',methods=['POST'])
def afterlogin():
    user = request.form['_id']
    passw = request.form['psw']
    print(user,passw)

    query = {'_id': {'seq': user}}

    docs = my_database.get_query_result(query)
    print(docs)

    print(len(docs.all()))

    if(len(docs.all())==0):
        return  render_template('login.html', pred='The Username is not found.')
    else:
        if ((user==docs[0][0]['_id'] and passw==docs[0][0]['psw'])):
            return render_template('prediction.html')
        else:
            print('Invalid User')


@app.route('/logout')
def logout():
    return render_template('logout.html')

@app.route('/prediction')
def prediction():
    return render_template('prediction.html')


@app.route('/result',methods=["GET","POST"])
def res():
    if request.method=="POST":
        f=request.files['image']
        basepath=os.path.dirname(__file__)
        filepath=os.path.join(basepath,'uploads',f.filename)
        f.save(filepath)

        img=image.load_img(filepath,target_size=(299,299))
        x=image.img_to_array(img)
        x=np.expand_dims(x,axis=0)
        #print(x)
        img_data=preprocess_input(x)
        prediction=np.argmax(model.predict(img_data),axis=1)

        index=['No Diabetic Retinopathy','Mild DR','Moderate DR','Sever DR','Proliferative DR']

        result = str(index[output[0]])
        return render_template('prediction.html',prediction=result)



if __name__  ==  "__main__" :
    app.run(debug=False)