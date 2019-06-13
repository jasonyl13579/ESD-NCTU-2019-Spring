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
database = 'online.sqlite'
x = 0
y = 0
count = 0
port = 6000
"""
Step1. Collect RSSI data
"""


APNumM1=4                                     #number of AP
APNumM2=8 
sampleNumM1=5
sampleNumM2=10                                #number of sampling
fingerPrintingNum=33                        #number of fingerprinting reference point
minNum=3                                  #KNN - K
#RSSICollect= np.full((APNum, sampleNum), -200, dtype=np.int)
RSSIList2= []
for i in range(APNumM2):
    RSSIList2.append([-100]*sampleNumM2)
RSSIList1= []
for i in range(4):
    RSSIList1.append([-100]*sampleNumM1)
#以下為已知，training過的資料
RSSITrue = np.load('rssi.npy')
xyList = np.load('xy.npy')
#xList=np.array([0]*fingerPrintingNum)       
#yList=np.array([0]*fingerPrintingNum)
#RSSITrue=np.array([[-10,-10,-10,-10,-10,-10,-10,-10]]*fingerPrintingNum)#[[-10,-10,-10]]*fingerPrintingNum


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

def process_rssi_M2(RSSICollect):
    RSSI=[]
    Dist=[]
    
    global xyList, RSSITrue, x, y
    for i  in range(0,APNumM2):
        RSSIavg=sum(RSSICollect[i])/sampleNumM2
        RSSI.append(RSSIavg)
    print(RSSI, file=sys.stderr)
    """
    Step3. Find smallest 5 Euclidean distance spot and delete the impossible ones
    """
    a = np.array(RSSI)
    for i in range(0,fingerPrintingNum):
        b = np.array(RSSITrue[i])
        #print(a,' ',b)
        dist = np.linalg.norm(a-b)
        #print(dist)
        Dist.append(dist)
    index=sorted(range(len(Dist)), key=lambda k: Dist[k])
    print(index, file=sys.stderr)
   # print(Dist, file=sys.stderr)
    
    """
    Step4. Weight KNN
    """
    #for i in range(0,minNum):
        #print(Dist[i])
    distSum=0
    X=0
    Y=0
    #take inverse to represent weights
    for i in range(0,minNum):
        distSum+=1/Dist[index[i]]
        X+=1/Dist[index[i]]*xyList[index[i]][0]
        Y+=1/Dist[index[i]]*xyList[index[i]][1]
    X/=distSum
    Y/=distSum
    x = X
    y = Y
    print("location: ",x," ",y, file=sys.stderr)
    return X, Y
def process_rssi_M1(RSSICollect):
    RSSI=[]
    
    global xyList, RSSITrue, x, y
    for i  in range(0,APNumM1):
        RSSIavg=sum(RSSICollect[i])/sampleNumM1
        RSSI.append(RSSIavg)
    print(RSSI, file=sys.stderr)
    index=sorted(range(len(RSSI)), key=lambda k: RSSI[k])
    index.reverse()
    print (index, file=sys.stderr)
    if index[0] == 2 and index[1] == 3:
        return 'A'
    elif index[0] == 3 and index[1] == 2:
        return 'A'
    elif index[0] == 1 and index[1] == 2:
        return 'B'
    elif index[0] == 2 and index[1] == 1:
        return 'B'
    else:
        return 'C'
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
@app.route('/M2', methods=['GET'])
def get_M2_text():
    x, y = process_rssi_M2(RSSIList2) 
    if (round(x,2) == 4.28 and round(y,2) == 0.65):
        return "Out,Side"
    return str(round(x,2)) + ', ' + str(round(y,2))
@app.route('/M1', methods=['GET'])
def get_M1_text():
    return str(process_rssi_M1(RSSIList1))
#def case(TYPE):
#    value = Counter(status).most_common(1)[0][0]
#    if TYPE == "graphic":
#            return (picture_path + str(value) + ".jpg") 
#    if TYPE == "text":
#                
#        return "case" + str(value)

@app.route('/ibeacon', methods=['POST'])
def label_post():
    app.logger.debug(request.json)
    if 'rssi' in request.json:
        rssis = request.json['rssi'].split(",")
        minors = request.json['minor'].split(",")
        major = int (request.json['major'])
        if 'type' in request.json and request.json['type'] == 4: # collecting phase
            db = get_db()
            cursor = db.cursor()
            
            multi = []
            for i in range(len(rssis)):
                multi.append([request.json['x'],request.json['y'],int(rssis[i]), major,int(minors[i]),datetime.now()])
            #cursor.execute("INSERT INTO IBEACON (X,Y,RSSI,MAJOR,MINOR,perfomed_at)\
            #  VALUES(?,?,?,?,?,?)", (request.json['x'],request.json['y'],request.json['rssi'],request.json['major'],request.json['minor'],datetime.now()))
            cursor.executemany("INSERT INTO IBEACON (X,Y,RSSI,MAJOR,MINOR,perfomed_at)\
              VALUES(?,?,?,?,?,?)", (multi))
            db.commit()
        else: #online phase
            global RSSIList1, RSSIList2
            if major == 2:
            
                for i in range(len(rssis)):
                    ap_index = int(minors[i]) - 1
                    if rssis[i] != "0":
                        RSSIList2[ap_index].append(float(rssis[i]))
                    else:
                        RSSIList2[ap_index].append(-100)
                    del RSSIList2[ap_index][0]
                
            if major == 1:
                
                for i in range(len(rssis)):
                    ap_index = int(minors[i]) - 1
                    if rssis[i] != "0":
                        RSSIList1[ap_index].append(float(rssis[i]))
                    else:
                        app.logger.debug("Zero")
                        RSSIList1[ap_index].append(-100)
                    del RSSIList1[ap_index][0]
                #app.logger.debug(process_rssi_M2(RSSIList1))
                #app.logger.debug(RSSIList2)
    
    return 'OK'
@app.route('/online', methods=['POST'])
def online_label_post():
    global RSSIList2
    app.logger.debug(request.json)
    if request.json['major'] == 2:
        ap_index = request.json['minor'] -1
        if request.json['rssi'] != 0:
            RSSIList2[ap_index].append(request.json['rssi'])
        else:
            RSSIList2[ap_index].append(-100)
        del RSSIList2[0]
    #process_rssi(np.array(RSSITrue))    
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
        opts, args = getopt.getopt(sys.argv[1:],"shldp:",["port"])
    except getopt.GetoptError:
        print ('Usage: server_training.py\n [-s] Enable prediction\n [-l] Enable global label\n [-d] Debug mode (Do not save data into database)\n [-p <port>] Port\n')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('Usage: server_training.py\n [-s] Enable prediction\n [-l] Enable global label\n [-d] Debug mode (Do not save data into database)\n [-p <port>] Port\n')
            sys.exit()
        if opt == '-s':
            enable_prediction = True
            load_lstm_model()
            print ("Enable_prediction.")
            print ("Using model: " + date)
        if opt == '-l':
            enable_global_label = True
            print ("Enable global label.")
        if opt == '-d':
            debug = True
            print ("Debug mode. (Do not save data into database)")    
        if opt == '-p':
            port = arg
    
    '''
    data = sio.loadmat('data/x_test.mat')
    x_test = data['x_test']
    y_pre = np.squeeze(model.predict(x_test), 0)
    print (y_pre)
    '''
    app.run(host='0.0.0.0', port = port, debug=True)