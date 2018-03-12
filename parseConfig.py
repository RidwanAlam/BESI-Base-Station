# this file contains functions related to parsing the user input provided in the config file

def parseConfig():
    ports = []
    useAccel = []
    useLight = []
    useADC = []
    useWeather = []
    basename = str('191.168.0.100')
    token = "1a79ee75e7328538f9df96bdc7e22f9d17ae398e"
    # Read config file
    fconfig = open("Configure.txt")
    
    for line in fconfig:
        #ignore comments
        if line[0] == "#":
            pass
        else:
            splitLine = line.split("=")
            try:
                if splitLine[0] == "xOff":
                    xOff = int(splitLine[1])
                    #print "xOff: ",xOff
            except:
                pass
                #print "Error processing x offset"
            
            try:
                if splitLine[0] == "yOff":
                    yOff = int(splitLine[1])
                    #print "yOff: ",yOff
            except:
                pass
                #print "Error processing y offset" 
            
            try:   
                if splitLine[0] == "zOff":
                    zOff = int(splitLine[1])
                    #print "zOff: ",zOff
            except:
                pass
                #print "Error processing z offset" 
            
            try:  
                if splitLine[0] == "xSens":
                    xSens = float(splitLine[1])
                    #print "xSens: ",xSens
            except:
                pass
                #print "Error processing x sensitivity" 
            
            try:    
                if splitLine[0] == "ySens":
                    ySens = float(splitLine[1])
                    #print "ySens: ",ySens
            except:
                pass
                #print "Error processing y sensitivity"
            
            try:   
                if splitLine[0] == "zSens":
                    zSens = float(splitLine[1])
                    #print "zSens: ",zSens
            except:
                pass
                #print "Error processing z sensitivity"
            
            try:
                if splitLine[0] == "ShimmerID_1":
                    ShimmerID1 = splitLine[1].rstrip()
                    #print "ShimmerID_1: ",ShimmerID1
            except:
                print "Error processing ShimmerID"
                
            try:
                if splitLine[0] == "ShimmerID_2":
                    ShimmerID2 = splitLine[1].rstrip()
                    #print "ShimmerID_2: ",ShimmerID2
            except:
                print "Error processing ShimmerID"
                
            try:
                if splitLine[0] == "ShimmerID_3":
                    ShimmerID3 = splitLine[1].rstrip()
                    #print "ShimmerID_3: ",ShimmerID3
            except:
                print "Error processing ShimmerID"
            
            try:
                if splitLine[0] == "PLOT":
                    PLOT = (splitLine[1] == "True\n")
                    #print "plot: ",PLOT
            except:
                print "Error processing plot command"
            
            try:    
                if splitLine[0] == "numRelayStat":
                    numRelayStat = int(splitLine[1])
                    #print "number of relay stations: ",numRelayStat
            except:
                print "Error processing the number of relay stations"
                
            try:
                if splitLine[0] == "DeploymentID":
                    DeploymentID = int(splitLine[1])
                    #print "deployment ID: ",DeploymentID
            except:
                print "Error processing deployment ID"
                
            try:
                if splitLine[0] == "fileLengthSec":
                    fileLengthSec = int(splitLine[1])
                    #print "file length (seconds): ",fileLengthSec
            except:
                print "Error processing file length"
                
            try:
                if splitLine[0] == "fileLengthDay":
                    fileLengthDay = int(splitLine[1])
                    #print "file length (days): ",fileLengthDay
            except:
                print "Error processing file length"
                
            try:
                if splitLine[0] == "networkNum":
                    networkNum = int(splitLine[1])
                    #print "Network Number (1-Wi-Fi, 0-LAN): ",networkNum
            except:
                print "Error processing network number"
            
            try:
                if splitLine[0] == "hostIP":
                    basename = str(splitLine[1].rstrip())
                    #print "IP: ",basename
            except:
                print "Error processing base-station IP"
             
            try:
                if splitLine[0] == "DeploymentToken":
                    token = str(splitLine[1].rstrip())
                    #print "IP: ",basename
            except:
                print "Error processing deployment token"

            try:
                if splitLine[0] == "NotificationTime":
                    notiTime = splitLine[1].split(":") #notiTime = ['hour', 'minute']

            except:
                print "Error processing notification time"
            
            try:   
                if splitLine[0] == "PORT":
                    ports.append(int(splitLine[1]))
                    
                elif splitLine[0] == "USE_ACCEL":
                    useAccel.append(splitLine[1] == "True\n")
                    
                elif splitLine[0] == "USE_LIGHT":
                    useLight.append(splitLine[1] == "True\n")
                    
                elif splitLine[0] == "USE_ADC":
                    useADC.append(splitLine[1] == "True\n")
                    
                elif splitLine[0] == "USE_WEATHER":
                    useWeather.append(splitLine[1] == "True\n")
            except:
                print "Error processing relay station parameters"
                
    return basename, ports, useAccel, useLight, useADC, useWeather, numRelayStat, fileLengthSec, fileLengthDay, DeploymentID, token, networkNum, notiTime