from datetime import datetime

# raw light data does not require any processing
# this function simply copies data and removes leading 0s         
def processLight(lightFile, port, DeploymentID):
    startDate =  lightFile.readline()
    empty = False
    
    # if the basestation gets any streaming data, the first line is a date and time
    try:
        dt = datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    except:
        print "Empty Light File"
        return None
        
    fname = "Data_Deployment_{0}/Relay_Station_{1}/Light/Ambient Light{2}_{3:02}-{4:02}.txt".format(DeploymentID, port, dt.date(), dt.time().hour, dt.time().minute, DeploymentID)
    outputFile = open(fname, "w")
    
    # write metadata
    outputFile.write(startDate)
    outputFile.write("Deployment ID: {0}, Relay Station ID: {1}\n".format(DeploymentID, port))
    outputFile.write("Timestamp,Light Level\n")
    
    for line in lightFile:
        try:
            lastTime, lightLevel, nLine = line.split(",")
        except:
            # incomplete line - ignore (should only occur on the last line)
            pass
        else:
            outputFile.write("{0:.2f},{1:.2f}\n".format(float(lastTime), float(lightLevel)))
            
    return fname

# produces a time series of light level data from a processed file
def plotLight(inFile):

    time_data = []
    light_data = []
    
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
            light_data.append(float(splitData[1]))
        except:
            print "error processing float"
            
    return time_data, light_data 

def plotLightTimeStamp(inFile):

    time_data = []
    light_data = []
    
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
            light_data.append(float(splitData[1]))
        except:
            print "error processing float"
            
    return time_data, light_data, dt