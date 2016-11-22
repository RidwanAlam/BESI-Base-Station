# parses config.txt for processing
# config.txt format is <key>=<value>
def processParseConfig():
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
                print "Error processing x offset"
            
            try:
                if splitLine[0] == "yOff":
                    yOff = int(splitLine[1])
                    #print "yOff: ",yOff
            except:
                print "Error processing y offset" 
            
            try:   
                if splitLine[0] == "zOff":
                    zOff = int(splitLine[1])
                    #print "zOff: ",zOff
            except:
                print "Error processing z offset" 
            
            try:  
                if splitLine[0] == "xSens":
                    xSens = float(splitLine[1])
                    #print "xSens: ",xSens
            except:
                print "Error processing x sensitivity" 
            
            try:    
                if splitLine[0] == "ySens":
                    ySens = float(splitLine[1])
                    #print "ySens: ",ySens
            except:
                print "Error processing y sensitivity"
            
            try:   
                if splitLine[0] == "zSens":
                    zSens = float(splitLine[1])
                    #print "zSens: ",zSens
            except:
                print "Error processing z sensitivity"
            
            try:
                if splitLine[0] == "DeploymentID":
                    DeploymentID = int(splitLine[1])
                    #print "deployment ID: ",DeploymentID
            except:
                print "Error processing deployment ID"
            
    return DeploymentID