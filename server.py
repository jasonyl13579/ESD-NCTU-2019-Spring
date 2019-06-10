# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 13:17:22 2018

@author: JasonHuang
"""
from flask import Flask, send_file, request, abort, g
import sys, getopt
import time
from collections import Counter
import numpy as np
import sqlite3
import io
import tensorflow as tf
from datetime import datetime
import scipy.io as sio
from keras.models import load_model
from keras.backend.tensorflow_backend import set_session
#from flask_script import Manager

app = Flask(__name__)
#manager = Manager(app)

#%% parameter to modify

#Offline
database = 'ibeacon.sqlite'
x = 0
y = 0
count = 0


#%% sqlite init
DATABASE = database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        # Enable foreign key check
        print ("Opened database successfully");
        db.execute("PRAGMA foreign_keys = ON")
    return db


#%%tensorflow

def tic():
    #Homemade version of matlab tic and toc functions
    global startTime_for_tictoc
    startTime_for_tictoc = time.time()

def toc():
    if 'startTime_for_tictoc' in globals():
        print("Elapsed time is " + str(time.time() - startTime_for_tictoc) + " seconds.")
    else:
        print("Toc: start time not set")
        
#%%sqlite array type
        
def adapt_array(arr):
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)

sqlite3.register_adapter(np.ndarray, adapt_array)
sqlite3.register_converter("array", convert_array)
#%% server
#app = Flask(__name__)
 
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

#@app.route('/graphic', methods=['GET'])
#def get_graphic():
#    filename = case("graphic")
#    return send_file(filename, mimetype='image/gif')
@app.route('/', methods=['GET'])
#@app.route('/text', methods=['GET'])
def get_text():
    data = {}
    data['x'] = x
    data['y'] = y
    return str(x) + ',' + str(y)
#def case(TYPE):
#    value = Counter(status).most_common(1)[0][0]
#    if TYPE == "graphic":
#            return (picture_path + str(value) + ".jpg") 
#    if TYPE == "text":
#                
#        return "case" + str(value)

@app.route('/ibeacon', methods=['POST'])
def change_label_post():
    global global_label
    app.logger.debug(request.json)
    
    if 'rssi' in request.json:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO IBEACON (X,Y,RSSI,MAJOR,MINOR,perfomed_at)\
          VALUES(?,?,?,?,?,?)", (request.json['x'],request.json['y'],request.json['rssi'],request.json['major'],request.json['minor'],datetime.now()))
        db.commit()
    
    return 'OK'
@app.route('/shutdown', methods=['POST'])
def shutdown():
    '''
    data['x_test'] = x
    data['y_test'] = y
    data['Count'] = count
    sio.savemat(mat_path, data)
    '''
    shutdown_server()
    return 'Server shutting down...'
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
    #print ("Close server.", file=sys.stderr)
if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv,"shld")
    except getopt.GetoptError:
        print ('server_training.py -s <enable server>')
        sys.exit(2)
    for opt in args:
        if opt == '-s':
            enable_prediction = True
            print ("Enable_prediction.")
        if opt == '-l':
            enable_global_label = True
            print ("Enable global label.")
        if opt == '-d':
            debug = True
            print ("Debug mode.")    
        if opt == '-h':
            print ('server_training.py -s <enable server>')
            sys.exit()
    
    '''
    data = sio.loadmat('data/x_test.mat')
    x_test = data['x_test']
    y_pre = np.squeeze(model.predict(x_test), 0)
    print (y_pre)
    '''
    app.run(host='0.0.0.0', port = 6000, debug=True)