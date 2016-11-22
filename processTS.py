# Goal: set a common start time for all the accel and door sensor files

import Tkinter as tk
import datetime

def processAccelTime(accelFile, port, DeploymentID, startTime):
    startDate =  accelFile.readline()
    
    # if the basestation gets any streaming data, the first line is a date and time
    try:
        dt = datetime.datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    except:
        print "Empty Accelerometer File"
        return 
   
    # file name is based on start date and time of session
    fname = "Data_Deployment_{0}/Relay_Station_{1}/Accelerometer/Accelerometer_Synched{2}_{3:02}-{4:02}.txt".format(DeploymentID, port, startTime.date(), startTime.time().hour, startTime.time().minute, DeploymentID)
    outputFile = open(fname, "w")
    
    outputFile.write(str(startTime) + '\n')
    outputFile.write("Deployment ID: {0}, Relay Station ID: {1}\n".format(DeploymentID, port))
    outputFile.write("Timestamp,X-Axis,Y-Axis,Z-Axis\n")
    
    # timeOffset is used to correct for periods when the connection is lost
    timeOffset = (dt - startTime).days * 86400 + (dt - startTime).seconds + (dt - startTime).microseconds/1000000.0
    
    for line in accelFile:
        splitLine = line.split(",")
        try:
            float(splitLine[0])
        except:
            print "error processing float in accel"
        else:
            t_data = float(splitLine[0])
            x_data = splitLine[1]
            y_data = splitLine[2]
            z_data = splitLine[3]
            rssi = splitLine[4]
        
            outputFile.write("{0:.5f},{1},{2},{3},{4}".format(t_data + timeOffset, x_data, y_data, z_data, rssi))
            
def processDoorTime(doorFile, port, DeploymentID, startTime):
    startDate =  doorFile.readline()
    
    # if the basestation gets any streaming data, the first line is a date and time
    try:
        dt = datetime.datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    except:
        print "Empty Door File"
        return
   
    # file name is based on start date and time of session
    fname = "Data_Deployment_{0}/Relay_Station_{1}/Door/Door Sensor_Synched{2}_{3:02}-{4:02}.txt".format(DeploymentID, port, startTime.date(), startTime.time().hour, startTime.time().minute, DeploymentID)
    outputFile = open(fname, "w")
    
    # write metadata
    outputFile.write(str(startTime) + " ")
    outputFile.write("Deployment ID: {0}, Relay Station ID: {1}\n".format(DeploymentID, port))
    outputFile.write("Timestamp,Door Sensor Channel 1, Door Sensor Channel 2\n")
    
    # timeOffset is used to correct for periods when the connection is lost
    timeOffset = (dt - startTime).days * 86400 + (dt - startTime).seconds + (dt - startTime).microseconds/1000000.0
    
    for line in doorFile:
        splitData = line.split(",")
        #print splitData
        try:
            t_data = float(splitData[0])
            door1_data = splitData[1]
            door2_data = splitData[2]
        except:
            print "error processing float"
        else:    
            outputFile.write("{0:.2f},{1},{2}".format(t_data + timeOffset, door1_data, door2_data))


taccel_data = []
x_data = []
y_data = []
z_data = []
tlight_data1 = []
light_data1 = []
tlight_data2 = []
light_data2 = []
tlight_data3 = []
light_data3 = []
tsound_data = []
sound_data = []
tTemp_data = []
temp_data = []
tdoor_data = []
door1_data = []
door2_data = []

root = tk.Tk()
root.withdraw()

downsampleRate = 1

accelLastTime = 0

deployID = 17
relayIDs = [9999]

startDatetime = "2016-04-21_15-03.txt"



startTimes = []

for relayStat in relayIDs:
    basePath = "Data_Deployment_" + str(deployID) + "/Relay_Station_" + str(relayStat) + "/"
    #for fileName in  listdir(basePath + "Door"):
    doorProcFile = open(basePath + "Door/" + "Door Sensor" + startDatetime, "r")
    startDate =  doorProcFile.readline()
    
    # if the basestation gets any streaming data, the first line is a date and time
    try:
        startTimes.append(datetime.datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f"))
    except:
        print "Empty Accelerometer File"
    
    doorProcFile.close()
    
startTime = min(startTimes)

for relayStat in relayIDs:
    basePath = "Data_Deployment_" + str(deployID) + "/Relay_Station_" + str(relayStat) + "/"
    #for fileName in  listdir(basePath + "Door"):
    doorProcFile = open(basePath + "Door/" + "Door Sensor" + startDatetime, "r")
    
    processDoorTime(doorProcFile, relayStat, deployID, startTime)
    
    doorProcFile.close()


for relayStat in relayIDs:
    basePath = "Data_Deployment_" + str(deployID) + "/Relay_Station_" + str(relayStat) + "/"
    #for fileName in  listdir(basePath + "Accelerometer"):
    accelProcFile = open(basePath + "Accelerometer/" + "Accelerometer" + startDatetime, "r")
    
    processAccelTime(accelProcFile, relayStat, deployID, startTime)
    
    accelProcFile.close()
