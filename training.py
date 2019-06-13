# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 17:31:27 2019

@author: User
"""

# build map
import sqlite3
from scipy import stats
import numpy as np
import math
conn = sqlite3.connect('online.sqlite', detect_types=sqlite3.PARSE_DECLTYPES)
print ("Opened database successfully");
c = conn.cursor()

#initialization
APNum = 8 #number of iBeacon
minor = np.array([1,2,3,4,5,6,7,8])
fingerPrintingNum = 33 # number of finger printing points

xyfield = [[0 for i in range(1)] for j in range(fingerPrintingNum)] #紀錄34組(x,y)
rssiMatrix = np.zeros((fingerPrintingNum, APNum)) #34個點，每個點有8個rssi值
major = 2

#建立(x,y)種類的list
j = 0
startDate = "2019-06-04"
endDate = "2019-06-05"
c.execute("SELECT X,Y FROM IBEACON WHERE perfomed_at BETWEEN '{sd}' AND '{ed}'".format(sd=startDate,ed=endDate))
xy = c.fetchall()
xyList = np.array(xy) #(x, y)
print("len of xy")
print(len(xy))
for i in range (0, len(xy)):
    if xy[i] in xyfield :
        pass
    elif xy[i][0] >=0 and xy[i][1] >=0: # (x,y)是未記錄過的
        print(xy[i])
        xyfield[j] = xy[i]
        j+=1
        
print("xyfield:")
print(xyfield)
#######################################################################################
#計算各點RSSI平均
#######################################################################################
for k in range (0, len(xyfield)):
    c.execute("SELECT RSSI,MAJOR,MINOR FROM IBEACON WHERE X = ? AND Y = ? AND perfomed_at BETWEEN '{sd}' AND '{ed}'".format(sd=startDate,ed=endDate), xyfield[k])
    rssiList = c.fetchall()
    rssiValue = np.zeros(APNum)
    
    minorList = [[0 for i in range(1)] for j in range(APNum)]

    #對minor進行分類
    for i in range (0, len(rssiList)) :
        if rssiList[i][1] == major and rssiList[i][0] != 0 :  #major=2
            if rssiList[i][2] == minor[0] : #minor=1
                minorList[0].append(rssiList[i][0])
                
            elif rssiList[i][2] == minor[1] : #minor=2
                minorList[1].append(rssiList[i][0])
                
            elif rssiList[i][2] == minor[2] : #minor=3
                minorList[2].append(rssiList[i][0])
                
            elif rssiList[i][2] == minor[3] : #minor=4
                minorList[3].append(rssiList[i][0])

            elif rssiList[i][2] == minor[4] : #minor=5
                minorList[4].append(rssiList[i][0])
                
            elif rssiList[i][2] == minor[5] : #minor=6
                minorList[5].append(rssiList[i][0])
                
            elif rssiList[i][2] == minor[6] : #minor=7
                minorList[6].append(rssiList[i][0])
                
            elif rssiList[i][2] == minor[7] : #minor=8
                minorList[7].append(rssiList[i][0])
                
            else :
                print(rssiList[i][1])
                print("minor error")
                
    
    #把List轉成np.array
    mean = np.zeros(APNum)
    for i in range(0,APNum):
        array = np.array(minorList[i])
        mean[i] = np.mean(array[1:])
    print("mean:")
    print(mean)
    
    ############################################
    # find trimmed mean with percentage = 0.25
    ############################################
    
    trim_mean = np.zeros(APNum)
    for i in range(0, APNum):
        trim_mean[i] = stats.trim_mean(minorList[i][1:],0.1)
        if math.isnan(trim_mean[i]):
            trim_mean[i] = -100
    print("trim_mean：")
    print(trim_mean)
    
    
    for i in range(0, APNum):
        rssiMatrix[k][i] = trim_mean[i]

########################################################################################

#Output: n個AP,m個點,mxn的RSSI矩陣
print("rssiMatrix:")
print(rssiMatrix)
np.save('rssi',rssiMatrix)
np.save('xy',xyfield)


