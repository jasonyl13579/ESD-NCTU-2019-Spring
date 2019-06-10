# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 18:06:06 2019

@author: Jason
"""

import sqlite3
import scipy.io as sio
import numpy as np
import io
from datetime import datetime, timedelta
#conn = sqlite3.connect('Presence_Detection.db')
conn = sqlite3.connect('ibeacon.sqlite', detect_types=sqlite3.PARSE_DECLTYPES)
print ("Opened database successfully");

c = conn.cursor()

#%% create db
def create_table(conn):
    c = conn.cursor()
    c.execute('''CREATE TABLE IBEACON
          (X INT DEFAULT -1,
          Y INT DEFAULT -1,
          RSSI INT DEFAULT -1,
          MAJOR INT DEFAULT -1,
          MINOR INT DEFAULT -1,
          perfomed_at TIMESTAMP DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'LOCALTIME'))
                );''')
    conn.commit()
    conn.close()
    
#create_table(conn)


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
multi = []

#%% save_CSI as mat

x = []
y = []
count = 0
data = {}
#https://stackoverflow.com/questions/27640857/best-way-to-store-python-datetime-time-in-a-sqlite3-column
#startDate = "2019-04-01 16:08:29"
startDate = "2019-05-01"
endDate = "2019-05-18"
startTime = "15:34:00"
endTime = "15:40:00"
#c.execute("SELECT * FROM PD")
#c.execute("SELECT * FROM IBEACON WHERE perfomed_at BETWEEN '{sd}' AND '{ed}'".format(sd=startDate,ed=endDate))
#c.execute("SELECT * FROM PD WHERE perfomed_at BETWEEN '{sd}' AND '{ed}' AND time(perfomed_at) BETWEEN '{st}' AND '{et}'".format(sd=startDate,ed=endDate,st=startTime,et=endTime))
#x, y = createTrain(c, 10)
#d = datetime(2019, 5, 9, 16, 25, 00, 000000)
#for row in c:
#    x.append(row[0])
#    y.append(row[1])
#    if row[2] - d > timedelta(seconds = 0) and row[2] - d < timedelta(seconds = 180):
#        print(row[2])
#        print(count)
#       # break
#    print(row[2])
#    count = count + 1
##c.execute("DELETE FROM PD WHERE perfomed_at BETWEEN '{sd}' AND '{ed}' AND time(perfomed_at) BETWEEN '{st}' AND '{et}'".format(sd=startDate,ed=endDate,st=startTime,et=endTime))
##conn.commit() 

#print("PD:" + str(count))

c.execute("SELECT * FROM IBEACON WHERE MAJOR = 2")
count = 0
t = c.fetchall()
tarray = np.array(t)
print (tarray[0][2])
print (np.array(t))
for row in c:
    print (row[2])
    count = count + 1
print ("Change:" + str(count))


#sio.savemat(mat_path, data)
#c.execute("DELETE from IBEACON")
#conn.commit()
#data = c.fetchone()
conn.close()