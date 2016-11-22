from streamUtils import connectRecv
from datetime import datetime
from processSession import processSession
from parameters import LOST_CONN_TIMEOUT
from streamAccel import update_accel
from streamLight import update_light
from streamSound import update_sound
from streamTemp import update_temp
from streamDoor import update_door

# better implementation of the process to get data from each relay station
# currently not used



class Streamer:
    
    def __init__(self, queue, Port, useAccel, useLight, useADC, ShimmerIDs, plot, fileLengthSec, fileLengthDay, DeploymentID):
        self.port = Port
        self.useAccel = useAccel
        self.useLight = useLight
        self.useADC = useADC
        self.shimmerIDs =ShimmerIDs
        self.plot = plot
        self.fileLengthSec = fileLengthSec
        self.fileLengthDay = fileLengthDay
        self.deploymentID = DeploymentID
        self.t = []
        self.x = []
        self.y = []
        self.z = []
        self.light = []
        self.sound= []
        self.temp = []
        self.door1 = []
        self.door2 = []
        self.conectionAccel = None
        self.connectionLight = None
        self.connectionSound = None
        self.connectionTemp = None
        self.connectionDoor = None
        self.connected = 0
        self.accelFile = None
        self.lightFile = None
        self.soundFile = None
        self.tempFile = None
        self.doorFile = None
        self.sensorTimeouts = [0] * 5
        self.q = queue
        self.shimmerConnected = False
        
    # connect to the relay station specified in port    
    def connectToRS(self):
        # send info to the BBB: Shimmer Bluetooth ID and what sensors to use
        # this uses the same port as the accelerometer and closes it after sending the info
        try:
            self.connectionAccel = connectRecv(self.port)
            configMsg = "{},{},{},{},{},{},".format(self.useAccel, self.useADC, self.useLight, self.shimmerIDs[0], self.shimmerIDs[1], self.shimmerIDs[2])
            self.connectionAccel.sendall("{:03}".format(len(configMsg)) + configMsg)
            self.connectionAccel.close()
        except:
            pass
        
        # establish socket connections for each sensor used
        if self.useAccel:
            self.conectionAccel = connectRecv(self.port)
            self.accelFile = open("Data_Deployment_{}/relay_Station_{}/accel{}".format(self.deploymentID, self.port, self.port), "w")
        else:
            self.connectionAccel = None
            
        if self.useLight:
            self.connectionLight = connectRecv(self.port + 1)
            self.lightFile = open("Data_Deployment_{}/relay_Station_{}/light{}".format(self.deploymentID, self.port, self.port), "w")
        else:
            self.connectionLight = None
            
        if self.useADC:
            self.connectionSound = connectRecv(self.port + 2)
            self.connectionTemp = connectRecv(self.port + 3)
            self.connectionDoor = connectRecv(self.port + 4)
            self.soundFile = open("Data_Deployment_{}/relay_Station_{}/sound{}".format(self.deploymentID, self.port, self.port), "w")
            self.tempFile = open("Data_Deployment_{}/relay_Station_{}/temp{}".format(self.deploymentID, self.port, self.port), "w")
            self.doorFile = open("Data_Deployment_{}/relay_Station_{}/door{}".format(self.deploymentID, self.port, self.port), "w")
        else:
            self.connectionSound = None
            self.connectionTemp = None
            self.connectionDoor = None
            
        self.connected = 2

    # check for new data and add it to arrays to plot
    def streamUpdate(self, plotStartTime):
        
        plotCurrTime = datetime.now()
        # periodically process the raw data received and open new raw data files (old ones are deleted)
        if (((plotCurrTime - plotStartTime).seconds == self.fileLengthSec) and ((plotCurrTime - plotStartTime).days == self.fileLengthDay) or self.connected == 0):
            plotStartTime = datetime.now()
            if self.useAccel:
                self.accelFile.close()
                
            if self.useADC:
                self.soundFile.close()
                self.tempFile.close()
                self.doorFile.close()
                
            if self.useLight:
                self.lightFile.close()
            
            processSession(self.port)
            
            if self.useAccel:
                self.accelFile = open("Data_Deployment_{}/relay_Station_{}/accel{}".format(self.deploymentID, self.port, self.port), "w")
                
            if self.useADC:
                self.soundFile = open("Data_Deployment_{}/relay_Station_{}/sound{}".format(self.deploymentID, self.port, self.port), "w")
                self.tempFile = open("Data_Deployment_{}/relay_Station_{}/temp{}".format(self.deploymentID, self.port, self.port), "w")
                self.doorFile = open("Data_Deployment_{}/relay_Station_{}/door{}".format(self.deploymentID, self.port, self.port), "w")
                
            if self.useLight:
                self.lightFile = open("Data_Deployment_{}/relay_Station_{}/light{}".format(self.deploymentID, self.port, self.port), "w")
        
        # if connection is lost, wait set up the port to listen for the reconnect from the relay station
        if self.connected == 0:
            self.connected = 1
            
            self.connectToRS()
            self.OnLightConnect()
            self.OnSoundConnect()
            self.OnTempConnect()
            self.OnDoorConnect()
            
            self.connected = 2
    
    # runs update functions for each sensor used
    # update functions check if data is ready and update the plot if it is        
    def plotUpdate(self):
        # sensorTimeouts is used to to check if no messages have been received about a particular sensor for a period of time 
        # every time update_<sensor> is called and there is no data waiting sensorTimeout is incremented. When sensorTimeout reaches somethreshold, an alert is triggered
        # update accel
        if self.useAccel:
            if (update_accel(self.conectionAccel, self.accelFile, self.t, self.x, self.y, self.z) == 1):
                self.sensorTimeouts[0] = self.sensorTimeouts[0] + 1
            
            # if we received data 0,0,0 the Shimmer is not connected    
            elif self.x[-1]== 0 and self.y[-1]== 0 and self.z[-1]== 0:
                self.sensorTimeouts[0] = self.sensorTimeouts[0] + 1
                
            else:
                if not self.shimmerConnected:
                    
                    self.OnAccelConnect()
                self.sensorTimeouts[0] = 0
                
            if self.sensorTimeouts[0] == 10 * LOST_CONN_TIMEOUT:
                self.lostAccelConnect()
        
        # update light
        if self.useLight:
            if (update_light(self.connectionLight, self.lightFile, self.light) == 1):
                self.sensorTimeouts[1] = self.sensorTimeouts[1] + 1
                
            else:
                self.sensorTimeouts[1] = 0
                
            if self.sensorTimeouts[1] == LOST_CONN_TIMEOUT:
                self.lostLightConnect()
                
                
                #############################################################
                #Reset if connection lost (use light sensor to measure this)#
                #############################################################
                self.connected = 0
            
                
                
        # update ADC (noise, temp, and door)
        if self.useADC:
            if (update_sound(self.connectionSound, self.soundFile, self.sound) == 1):
                self.sensorTimeouts[2] = self.sensorTimeouts[2] + 1   
            else:
                self.sensorTimeouts[2] = 0
            if self.sensorTimeouts[2] == 10 * LOST_CONN_TIMEOUT:
                self.lostSoundConnect()
                
            if (update_temp(self.connectionTemp, self.tempFile, self.temp) == 1):
                self.sensorTimeouts[3] = self.sensorTimeouts[3] + 1
            else:
                self.sensorTimeouts[3] = 0 
            if self.sensorTimeouts[3] == LOST_CONN_TIMEOUT:
                self.lostTempConnect()
                
            if (update_door(self.connectionDoor, self.doorFile, self.door1, self.door2) == 1):
                self.sensorTimeouts[4] = self.sensorTimeouts[4] + 1 
            else:
                self.sensorTimeouts[4] = 0 
            if self.sensorTimeouts[4] == 10 * LOST_CONN_TIMEOUT:
                self.lostDoorConnect()

            
    def exitStreamer(self):
        self.accelFile.close()
        self.lightFile.close()
        self.soundFile.close()
        self.tempFile.close()
        self.doorFile.close()
        processSession(self.port)
        print "Exiting {}".format(self.port)
    
    
    # notify monitoring process   
    def lostAccelConnect(self):
        self.shimmerConnected = False
        print "no connection to acclerometer"
        self.q.put(["{0},accelLost".format(self.port)])
        self.sensorTimeouts[0] = 0
    
        
    def lostLightConnect(self):
        print "no connection to Light Sensor"
        self.q.put(["{0},lightLost".format(self.port)])
        
        # light sensor is used to check if we are still connected to 
        #the relay station because it is the least likely to not send data
        self.connected = 0
        self.sensorTimeouts[1] = 0
        
        
    def lostSoundConnect(self):
        print "no connection to Microphone"
        self.q.put(["{0},soundLost".format(self.port)])
        self.sensorTimeouts[2] = 0
        
        
    def lostTempConnect(self):
        print "no connection to temperature sensor"
        self.q.put(["{0},tempLost".format(self.port)])
        self.sensorTimeouts[3] = 0
        
        
    def lostDoorConnect(self):
        print "no connection to door sensor"
        self.q.put(["{0},doorLost".format(self.port)])
        self.sensorTimeouts[4] = 0
        
        
    def OnAccelConnect(self):
        self.shimmerConnected = True
        print "connection to acclerometer"
        self.q.put(["{0},accelConn".format(self.port)])
        self.sensorTimeouts[0] = 0
        
        
    def OnLightConnect(self):
        print "connection to Light Sensor"
        self.q.put(["{0},lightConn".format(self.port)])
        self.sensorTimeouts[1] = 0
        
        
    def OnSoundConnect(self):
        print "connection to Microphone"
        self.q.put(["{0},soundConn".format(self.port)])
        self.sensorTimeouts[2] = 0
        
        
    def OnTempConnect(self):
        print "connection to temperature Sensor"
        self.q.put(["{0},tempConn".format(self.port)])
        self.sensorTimeouts[3] = 0
        
        
    def OnDoorConnect(self):
        print "connection to door sensor"
        self.q.put(["{0},doorConn".format(self.port)])
        self.sensorTimeouts[4] = 0