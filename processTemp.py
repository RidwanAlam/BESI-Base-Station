from datetime import datetime

# low pass filter y[n] = .9y[n-1] + .1x[n]
def lowPassFilter(unfilteredData):
    filteredData = []
    if len(unfilteredData) > 2:
        filteredData.append(unfilteredData[0])
        
        for i in range(len(unfilteredData) - 1):
            filteredData.append(0.93 * filteredData[i] + 0.07 * unfilteredData[i + 1])
        
    else:
        filteredData = unfilteredData
    return filteredData

# processes timestamps from a file of raw temp. data
# the raw timestamp is the time since the start
# (in previous version the timestamp was the time since the last sample)
def processTemp(tempFile, port, DeploymentID):
    lastTime = 0.0
    empty = False
    #first line is the start date/time of the data collection
    startDate =  tempFile.readline()
    
    # if the first line is not a datetime, the file is empty and we have nothing to plot
    try:
        dt = datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    except:
        print "Empty Temperature File"
        return None
    
    fname = "Data_Deployment_{0}/Relay_Station_{1}/Temperature/Temperature{2}_{3:02}-{4:02}.txt".format(DeploymentID, port, dt.date(), dt.time().hour, dt.time().minute, DeploymentID)
    outputFile = open(fname, "w")
    
    # write metadata
    outputFile.write(startDate)
    outputFile.write("Deployment ID: {0}, Relay Station ID: {1}\n".format(DeploymentID, port))
    outputFile.write("Timestamp,Degree C,Degree F\n")
    
    for line in tempFile:
        try:
            lastTime, tempDataC, tempDataF, nLine = line.split(",")
        except:
            # incomplete line - ignore
            pass
        else:
            # add timeDelta to the timestamp of the last sample to get the timestamp of the current sample
            #lastTime = lastTime + float(timeDelta)
            outputFile.write("{0},{1},{2}\n".format(float(lastTime), tempDataC, tempDataF))
            
    return fname


# produces a time series of noise level data from a processed file
def plotTemp(inFile):

    time_data = []
    temp_data = []

    # first line is the start date and time
    inFile.readline()
    
    # ignore line with metadata 
    inFile.readline()
    inFile.readline()
    
    for line in inFile:
        splitData = line.split(",")
        #print splitData
        try:
            # splitData is [<time>,<deg. C>, <deg. F>]
            time_data.append(float(splitData[0]))
            temp_data.append(float(splitData[2]))
        except:
            print "error processing float"

    return time_data, temp_data

def plotTempStartTime(inFile):

    time_data = []
    temp_data = []

    # first line is the start date and time
    startDate = inFile.readline()
    
    # if the basestation gets any streaming data, the first line is a date and time
    try:
        dt = datetime.strptime(startDate.rstrip(), "%Y-%m-%d %H:%M:%S.%f")
    except:
        print "Empty Temperature File"
        return None
    
    # ignore line with metadata 
    inFile.readline()
    inFile.readline()
    
    for line in inFile:
        splitData = line.split(",")
        #print splitData
        try:
            # splitData is [<time>,<deg. C>, <deg. F>]
            time_data.append(float(splitData[0]))
            temp_data.append(float(splitData[2]))
        except:
            print "error processing float"

    return time_data, temp_data, dt