# functions to process raw Shimmer3 accelerometer data and produce arrays of timestamps and data to plot
from datetime import datetime
import math
from parameters import *
import struct

# computes the calibrated accelerometer magnitude from raw measurements for each axis
def calibrateMagnitude(t, x, y, z, calibSession):
    
    # these variables are used to account for corrupted packets
    last_valid = False
    t_last = 0
    invalid_count = 0
    
    x_calib = []
    y_calib = []
    z_calib = []
    accelMag = []
    
    remove_corrupted = True
    
    # a reading of 0 indicates no connection
    # if remove_corrupted is True, invalid entries (due to lost or currupted packets) are replaced with 0s
    for i in range(len(x)):
        # check if the last timestamp is valid and if the current is the last plus 320 (or + 640 if the shimmer misses a sample)
        if (not remove_corrupted or (not last_valid) or (int(t[i]) == int(t_last) + TICKS_PER_SAMPLE) or (int(t[i]) == int(t_last) + 2 * TICKS_PER_SAMPLE) or (int(t[i]) == int(t_last) + TICKS_PER_SAMPLE - SHIMMER_TICKS) or (int(t[i]) == int(t_last) + 2 * TICKS_PER_SAMPLE - SHIMMER_TICKS)):
            last_valid = True
            #t_last = t[i]
            if (x[i] != 0):
                x_calib.append((x[i] - calibSession.xOff)/calibSession.xSens)
            else:
                x_calib.append(0)
                
            if (y[i] != 0):
                y_calib.append((y[i] - calibSession.yOff)/calibSession.ySens)
            else:
                y_calib.append(0)
                
            if (z[i] != 0):
                z_calib.append((z[i] - calibSession.zOff)/calibSession.zSens)
            else:
                z_calib.append(0)
                
            accelMag.append(math.sqrt(x_calib[-1]**2 + y_calib[-1]**2 + z_calib[-1]**2))
            
        else:
            # corrupted packet - ignore 16 readings and write 0s instead
            # TODO: use more intelligent method to check the number of corrupted samples
            accelMag.append(0)
            invalid_count = invalid_count + 1
            print t_last
            print t[i]
            if invalid_count == CORRUPTED_COUNT:
                invalid_count = 0
                last_valid = False
        
    return accelMag
  

  
# reads a file of accelerometer data and returns arrays of timestamps, x, y, and z-axes to be plotted
def plotAccel(inFile):
    t_data = []
    x_data = []
    y_data = []
    z_data = []
    rssi_data = []
    
    # first line holds the start date and time
    startDate =  inFile.readline()
    
    # ignore line with metadata 
    inFile.readline()
    inFile.readline()
    
    for line in inFile:
        splitLine = line.split(",")
        try:
            float(splitLine[0])
        except:
            print "error processing float"
        else:
            t_data.append(float(splitLine[0]))
            x_data.append(float(splitLine[1]))
            y_data.append(float(splitLine[2]))
            z_data.append(float(splitLine[3]))
            rssi_data.append(int(splitLine[4]))
            
    return t_data, x_data, y_data, z_data, rssi_data

# same as plotAccel, but alos returns start time
def plotAccelStartTime(inFile):
    t_data = []
    x_data = []
    y_data = []
    z_data = []
    rssi_data = []
    
    # first line holds the start date and time
    startDate =  inFile.readline()
    
    try:
        dt = datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    except:
        print "Empty Light File"
        return None
    
    # ignore line with metadata 
    inFile.readline()
    inFile.readline()
    
    for line in inFile:
        splitLine = line.split(",")
        #print splitLine
        try:
            float(splitLine[0])
            float(splitLine[1])
            float(splitLine[2])
            float(splitLine[3])
            float(splitLine[4])
            
        except:
            print "error processing float"
        else:
            t_data.append(float(splitLine[0]))
            x_data.append(float(splitLine[1]))
            y_data.append(float(splitLine[2]))
            z_data.append(float(splitLine[3]))
            rssi_data.append(int(splitLine[4]))
            
    return t_data, x_data, y_data, z_data, rssi_data, dt


# processes timestamps from shimmer and writes the results to a file
def processAccel(accelFile, port, DeploymentID):
    rawTime = []
    lastTime = 0
    empty = True
    
    # initial value needs to be > -640 so the first sample does not look like it is 2 samples after this
    lastRelTime = -10000
    startDate =  accelFile.readline()
    
    # if the basestation gets any streaming data, the first line is a date and time
    try:
        startTime = datetime.datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    except:
        print "Empty Accelerometer File"
        return None, []
   
    # file name is based on start date and time of session
    fname = "Data_Deployment_{0}/Relay_Station_{1}/Accelerometer/Accelerometer{2}_{3:02}-{4:02}.txt".format(DeploymentID, port, startTime.date(), startTime.time().hour, startTime.time().minute, DeploymentID)
    outputFile = open(fname, "w")
    
    outputFile.write(startDate + "\n")
    outputFile.write("Deployment ID: {0}, Relay Station ID: {1}\n".format(DeploymentID, port))
    outputFile.write("Timestamp,X-Axis,Y-Axis,Z-Axis\n")
    
    # timeOffset is used to correct for periods when the connection is lost
    timeOffset = 0
    
    
    
    for line in accelFile:
        empty = False
        data = line.split(",")
        try:
            relTime, xAxis, yAxis, zAxis, rssi, nLine = data
        except: # line is a datetime object or an incomplete line
            try:
                dt = datetime.strptime(line.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
            except:
                pass
            else:
                # write datetime timestamp
                #outputFile.write(data[0])
                #print "found a date"
                # time is reset for each disconnect event
                timeOffset = (dt - startTime).days * 86400 + (dt - startTime).seconds + (dt - startTime).microseconds/1000000.0
                #print timeOffset
                lastTime = 0
        else:
            # for each valid data entry, the time stamp is incremented by the time between samples
            # check for a single missed sample
            if (int(relTime) == lastRelTime + 2 * TICKS_PER_SAMPLE) or (int(relTime) == lastRelTime + 2 * TICKS_PER_SAMPLE - SHIMMER_TICKS):
                lastTime = lastTime + 2 * TICK_TIME
            else:
                lastTime = lastTime + TICK_TIME
            # t is the raw timestamps from shimmer
            rawTime.append(relTime)
            lastRelTime = int(relTime)
            outputFile.write("{0:.5f},{1},{2},{3},{4}\n".format(float(lastTime) + timeOffset, int(xAxis), int(yAxis), int(zAxis), int(rssi)))
            
    if empty:
        outputFile.write("{0:.2f},{1},{2},{3},{4}\n".format(0, 0, 0, 0,))
            
    return fname, rawTime

# processes timestamps from shimmer and writes the results to a file
def processAccel_byte(accelFile, port, DeploymentID):
    rawTime = []
    lastTime = 0
    empty = True
    
    # initial value needs to be > -640 so the first sample does not look like it is 2 samples after this
    lastRelTime = -10000
    lastValidRelTime = -10000
    startDate =  accelFile.readline()
    # if the basestation gets any streaming data, the first line is a date and time
    try:
        startTime = datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    except:
        print "Empty Accelerometer File"
        return None, []
   
    # file name is based on start date and time of session
    fname = "Data_Deployment_{0}/Relay_Station_{1}/Accelerometer/Accelerometer{2}_{3:02}-{4:02}.txt".format(DeploymentID, port, startTime.date(), startTime.time().hour, startTime.time().minute, DeploymentID)
    outputFile = open(fname, "w")
    
    outputFile.write(startDate)
    outputFile.write("Deployment ID: {0}, Relay Station ID: {1}\n".format(DeploymentID, port))
    outputFile.write("Timestamp,X-Axis,Y-Axis,Z-Axis\n")
    
    # timeOffset is used to correct for periods when the connection is lost
    timeOffset = 0
    # Shimmer tick timestamp on the first sample
    startTick = -1
    # number of times the shimmer clock has rolled over form 65535 to 0
    numRollover = 0
    rolloverCount = 0
    isValid = True
    
    ind = 0
    last_line = ""
    #print len(accelFile.read().split("~~"))
    for line in accelFile.read().split("~~"):
        empty = False
        # an extra byte ("\r") is added to "\n"
        
        currupt_count = 0
        tmp_line = line
        
        # handle data that contains "~~"
        if len(line.replace("\r\n", "\n")) < 10:
            
            line = (last_line + "~~" + line).replace("\r\n", "\n")
       
        last_line = tmp_line
        
        
        
        
        
        try:
            dt = datetime.strptime(line.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
        except:
            try:
                (relTime, xAxis, yAxis, zAxis, rssi) = struct.unpack("HHHHh", line.replace("\r\n", "\n"))
            except:
                pass
                #print "accel process error {}".format(len(line)),line
            else:
                dataValid = ((int(xAxis) < 4096) and (int(yAxis) < 4096) and (int(zAxis) < 4096))
                #timestampValid = ((int(relTime) == lastRelTime + 2 * TICKS_PER_SAMPLE) or (int(relTime) == lastRelTime + 2 * TICKS_PER_SAMPLE - SHIMMER_TICKS)) or ((int(relTime) == lastRelTime +  TICKS_PER_SAMPLE) or (int(relTime) == lastRelTime + TICKS_PER_SAMPLE - SHIMMER_TICKS))
                timestampValid = (int(relTime) - lastRelTime)%128 == 0
                isValid = (dataValid and timestampValid) or (dataValid and startTick == -1) 
                
                if isValid:
                    if startTick == -1:
                        startTick = relTime
                        
                    tickDiff = relTime - startTick
                    if relTime < lastValidRelTime:
                        numRollover = numRollover + 1
                        #print relTime, lastRelTime, lastTime

                        
                    lastTime = 2*numRollover + 1.0/32768*tickDiff + 1.0/128
                    """
                    if (int(relTime) == lastRelTime + 2 * TICKS_PER_SAMPLE) or (int(relTime) == lastRelTime + 2 * TICKS_PER_SAMPLE - SHIMMER_TICKS):
                        lastTime = lastTime + (2) * TICK_TIME
                    elif (int(relTime) == lastRelTime +  TICKS_PER_SAMPLE) or (int(relTime) == lastRelTime + TICKS_PER_SAMPLE - SHIMMER_TICKS):
                        lastTime = lastTime + (1 ) *TICK_TIME
                        currupt_count = 0
                        
                    elif (int(relTime) == lastRelTime + 384):
                        lastTime = lastTime + 2 * TICK_TIME
                        currupt_count = 0
                        
                    else:           
                        pass
                        #print lastTime,lastRelTime,(relTime, xAxis, yAxis, zAxis, rssi)
                        
                    # t is the raw timestamps from shimmer
                    rawTime.append(relTime)
                    lastRelTime = int(relTime)
                    """
                    if isValid:
                        outputFile.write("{0:.5f},{1},{2},{3},{4}\n".format(float(lastTime) + timeOffset, int(xAxis), int(yAxis), int(zAxis), int(rssi)))
                        lastValidRelTime = relTime
                    lastRelTime = relTime 
        else:
            # time is reset for each disconnect event
            timeOffset = (dt - startTime).days * 86400 + (dt - startTime).seconds + (dt - startTime).microseconds/1000000.0
            #print timeOffset
            lastTime = 0
            # Shimmer tick timestamp on the first sample
            startTick = -1
            # number of times the shimmer clock has rolled over form 65535 to 0
            numRollover = 0
            lastRelTime = -10000
            lastValidRelTime = -10000


