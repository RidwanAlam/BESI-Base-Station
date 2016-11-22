from processParseConfig import processParseConfig
from processAccel import processAccel, processAccel_byte
from processLight import processLight
from processNoise import processSound, processSound_byte
from processTemp import processTemp
from processDoor import processDoor, processDoor_byte

def processSession(basePort):
    # read config.txt to get the deployment ID
    try:
        DeploymentID = processParseConfig()
    except:
        print "Error reading configuration file"
        
    
    
    try:
        rawAccelFile = open("Data_Deployment_{}/relay_Station_{}/accel{}".format(DeploymentID, basePort, basePort), "rb")
        rawLightFile = open("Data_Deployment_{}/relay_Station_{}/light{}".format(DeploymentID, basePort, basePort), "r")
        rawNoiseFile = open("Data_Deployment_{}/relay_Station_{}/sound{}".format(DeploymentID, basePort, basePort), "rb")
        rawTempFile = open("Data_Deployment_{}/relay_Station_{}/temp{}".format(DeploymentID, basePort, basePort), "r")
        rawDoorFile = open("Data_Deployment_{}/relay_Station_{}/door{}".format(DeploymentID, basePort, basePort), "rb")
    except:
        print "Error opening raw data files"
        
    else:
        # processing is mostly creating timestamps relative to he start of the data collection
        # these functions produce files name sensor ID + date
        processAccel_byte(rawAccelFile, basePort, DeploymentID)
        fname2 = processLight(rawLightFile, basePort, DeploymentID)
        fname3 = processSound_byte(rawNoiseFile, basePort, DeploymentID)
        fname4 = processTemp(rawTempFile, basePort, DeploymentID)
        fname5 = processDoor_byte(rawDoorFile, basePort, DeploymentID)
        
        rawAccelFile.close()
        rawLightFile.close()
        rawNoiseFile.close()
        rawTempFile.close()
        rawDoorFile.close()