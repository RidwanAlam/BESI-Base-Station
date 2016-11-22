# the door sensor is connected to 2 ADC channels on the BBB
# For now the data is left as average amplitude over 0.1s as measured by the ADC
# processing to determine transition events will likely me done here 
from datetime import datetime
import struct

# raw door data does not require any processing
# this function simply copies data and removes leading 0s         
def processDoor(doorFile, port, DeploymentID):
    startDate =  doorFile.readline()
    empty = False
    
    # if the basestation gets any streaming data, the first line is a date and time
    try:
        dt = datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    except:
        print "Empty Door File"
        return None
        
    fname = "Data_Deployment_{0}/Relay_Station_{1}/Door/Door Sensor{2}_{3:02}-{4:02}.txt".format(DeploymentID, port, dt.date(), dt.time().hour, dt.time().minute, DeploymentID)
    outputFile = open(fname, "w")
    
    # write metadata
    outputFile.write(startDate)
    outputFile.write("Deployment ID: {0}, Relay Station ID: {1}\n".format(DeploymentID, port))
    outputFile.write("Timestamp,Door Sensor Channel 1, Door Sensor Channel 2\n")
    
    for line in doorFile:
        try:
            lastTime, door1, door2, nLine = line.split(",")
        except:
            # incomplete line - ignore (should only occur on the last line)
            pass
        else:
            outputFile.write("{0:.2f},{1:.2f},{2:.2f}\n".format(float(lastTime), float(door1), float(door2)))
            
    return fname


def processDoor_byte(doorFile, port, DeploymentID):
    startDate =  doorFile.readline()
    empty = False
    
    # if the basestation gets any streaming data, the first line is a date and time
    try:
        dt = datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    except:
        print "Empty Door File"
        return None
        
    fname = "Data_Deployment_{0}/Relay_Station_{1}/Door/Door Sensor{2}_{3:02}-{4:02}.txt".format(DeploymentID, port, dt.date(), dt.time().hour, dt.time().minute, DeploymentID)
    outputFile = open(fname, "w")
    
    # write metadata
    outputFile.write(startDate)
    outputFile.write("Deployment ID: {0}, Relay Station ID: {1}\n".format(DeploymentID, port))
    outputFile.write("Timestamp,Door Sensor Channel 1, Door Sensor Channel 2\n")
    
    for line in doorFile.read().split("~~"):
        try:
            lastTime, door1, door2, = struct.unpack("fff", line.replace("\r\n", "\n"))
        except:
            # incomplete line - ignore (should only occur on the last line)
            pass
        else:
            outputFile.write("{0:.2f},{1:.2f},{2:.2f}\n".format(lastTime, door1, door2))
            
    return fname


# produces a time series of light level data from a processed file
def plotDoor(inFile):

    time_data = []
    door1_data = []
    door2_data = []
    
    # first line is the start date and time
    inFile.readline()
    
    # ignore line with metadata 
    inFile.readline()
    inFile.readline()
    
    for line in inFile:
        splitData = line.split(",")
        #print splitData
        try:
            time_data.append(float(splitData[0]))
            door1_data.append(float(splitData[1]))
            door2_data.append(float(splitData[2]))
        except:
            print "error processing float"
            
    return time_data, door1_data, door2_data

def plotDoorStartTime(inFile):

    time_data = []
    door1_data = []
    door2_data = []
    
    # first line is the start date and time
    startDate = inFile.readline()
    
    # if the basestation gets any streaming data, the first line is a date and time
    try:
        dt = datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    except:
        print "Empty Light File"
        return None
    
    # ignore line with metadata 
    inFile.readline()
    inFile.readline()
    
    for line in inFile:
        splitData = line.split(",")
        #print splitData
        try:
            time_data.append(float(splitData[0]))
            door1_data.append(float(splitData[1]))
            door2_data.append(float(splitData[2]))
        except:
            print "error processing float"
            
    return time_data, door1_data, door2_data, dt