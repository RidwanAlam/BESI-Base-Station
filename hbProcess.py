# the stream_process function receives and plots sensor data from a single BBB
from datetime import datetime
from hbProcUtils import *
from parameters import *
from processSession import processSession
from colorama import init
import time
import os
from uploadEvents import *
import globalParams
# NOTE: colorama does not work when run from eclipse

# global agiStatus
# global agiType
# global agiIndx
# initialize file names so they can be accessed in the update() function
faccel = None
soundFile = None
tempFile = None
doorFile = None
flight = None
plotStartTime = None
sensorTimeouts = [0] * 5 #tracks time since last packet received for each sensor
# connection status indicator:
# 0 - disconnected
# 1 - connection in progress
# 2 - connected
connected = 0

# agiIndx = 0
# agiType = 0
# agiStatus = False


# receives data from the BBB using a different socket for each sensor
# the port number for the accelerometer is given, and the other sockets are consecutive numbers following PORT
def heartbeat_process(commQueue = None, PORT = 9999, fileLengthSec = 600, fileLengthDay = 0, DeploymentID = 1, DeploymentToken="1a79ee75e7328538f9df96bdc7e22f9d17ae398e", networkNum = 1, ProcNum = 0, lock=None, host='191.168.0.100'):
    

    #
#     global connection
#     global connection2
#     global connection3
#     global connection4
#     global connection5
    
#     global agiStatus
#     global agiType
#     global agiIndx
    #localAgiStatus = heartbeats.agiStatus
    #localAgiType = heartbeats.agiType
    #localAgiIndx = heartbeats.agiIndx
    
    
    sensorList=['Audio','Door','Temperature','Light','Weather','Wearable']
    sensorFiles=[]
    relay_station_folder = "Data_Deployment_{0}/Node_{1:05}/".format(DeploymentID, PORT)
    if not os.path.exists(relay_station_folder):
        os.mkdir(relay_station_folder)  
    
    hbStatFileName = relay_station_folder + 'heartbeatStat.txt'
        
    for modality in sensorList:
        modality_folder = relay_station_folder + modality
        if not os.path.exists(modality_folder):
            os.mkdir(modality_folder)
        sensorFileName = modality_folder +"/HB_"+ modality +".txt"
        sensorFiles.append(sensorFileName)
        if (modality=='Weather'):
            with open(sensorFileName, "a") as heartFile:
                heartFile.write("timestamp, Humidity_HB, Pressure_HB, Temperature_HB \n")
        elif (modality=='Door'):
            with open(sensorFileName, "a") as heartFile:
                heartFile.write("timestamp, Door1_HB, Door2_HB \n")
        elif (modality=='Wearable'):
            with open(sensorFileName, "a") as heartFile:
                heartFile.write("Mode, timestamp, Wearable_HB, Battery_HB \n")
        else:
            with open(sensorFileName, "a") as heartFile:
                heartFile.write("timestamp, {}_HB \n".format(modality))

    #if not os.path.exists(relay_station_folder + "Accelerometer"):
    #    os.mkdir(relay_station_folder + "Accelerometer")
    #if not os.path.exists(relay_station_folder + "Temperature"):
    #    os.mkdir(relay_station_folder + "Temperature")
    #    rTempFile = relay_station_folder + "Temperature/" + "HB_temp.txt"
    #if not os.path.exists(relay_station_folder + "Light"):
    #    os.mkdir(relay_station_folder + "Light")
    #    rLightFile = relay_station_folder + "Light/" + "HB_light.txt"
    #if not os.path.exists(relay_station_folder + "Audio"):
    #    os.mkdir(relay_station_folder + "Audio")
    #    rAudioFile = relay_station_folder + "Audio/" + "HB_audio.txt"
    #if not os.path.exists(relay_station_folder + "Door"):
    #    os.mkdir(relay_station_folder + "Door")
    #    rDoorFile = relay_station_folder + "Door/" + "HB_door.txt"
    #if not os.path.exists(relay_station_folder + "Humidity"):
    #    os.mkdir(relay_station_folder + "Humidity")
    #    rHumFile = relay_station_folder + "Humidity/" + "HB_hum.txt"
    #if not os.path.exists(relay_station_folder + "Pressure"):
    #    os.mkdir(relay_station_folder + "Pressure")
    #    rPresFile = relay_station_folder + "Pressure/" + "HB_pres.txt"
    #if not os.path.exists(relay_station_folder + "Motion"):
    #    os.mkdir(relay_station_folder + "Motion")
    #    rMotionFile = relay_station_folder + "Motion/" + "HB_motion.txt"
    #if not os.path.exists(relay_station_folder + "Memento"):
    #    os.mkdir(relay_station_folder + "Memento")
    #    rMementoFile = relay_station_folder + "Memento/" + "HB_memento.txt"
    

    
    
    
    #printOffset = ProcNum*(len(sensorList)+1) + 1 
    # 4 lines: Node ID, Sensor name, Time, Value1, Value2
    printOffset = ProcNum*10 + 1 
    # need locks around print statements from each process to get them to display in the correct location
    #######################################
    # critical section
    lock.acquire()
    
    col_names = ['Sensors']+sensorList[0:4]+['Humidity','Pressure']+[sensorList[-1]]+['Agitation']
    row_format ='{:^13}' * len(col_names)
    # colorama init
    init()
    # Colorama is used to set curse position for printing
    # format is \x1b[y;xH where y = position down, x = position across   
    print '\x1b[{};1H'.format(printOffset + 0)
    #print '-------------- NODE {} --------------'.format(PORT)
    print '{:-^120}'.format('NODE '+ str(PORT))
    
    print '\x1b[{};1H'.format(printOffset + 2)
    print row_format.format(*col_names)
    
    time_entry = ['Time'] + [''] * (len(col_names)-1)
    print '\x1b[{};1H'.format(printOffset + 4)
    print row_format.format(*time_entry)
    
    value_entry = ['Value'] + [''] * (len(col_names)-1)
    print '\x1b[{};1H'.format(printOffset + 6)
    print row_format.format(*value_entry)
    
    value2_entry = ['--'] + [''] * (len(col_names)-1)
    print '\x1b[{};1H'.format(printOffset + 8)
    print row_format.format(*value2_entry)
    
     ####################################
    # end of critial section  
    
    lock.release() 


    
    #rHeartBeatFolder = "Data_Deployment_{}/Relay_Station_{}/HeartBeat/".format(DeploymentID, PORT)
    #rHeartBeatFileName = rHeartBeatFolder + "updates.txt"    
    while True:
        
        #try:
        connection = connectRecv(host, PORT, networkNum, None)
        connection.settimeout(5)
        # format is <sensor name> <number of samples>
        sensorStatus = connection.recv(1024).split(";")
        
#         localAgiStatus = heartbeats.agiStatus
#         localAgiType = heartbeats.agiType
#         localAgiIndx = heartbeats.agiIndx

        
        #######################################
        # critical section
        lock.acquire()
        # print update based on sensor and message from relay station
        if len(sensorStatus) >= 1:
            currtime = datetime.now()
            if (sensorStatus[0] == "starting up") or (sensorStatus[0] == "Connection Up!"):
                time_entry = ['Time'] + [currtime.strftime("%d %H:%M:%S")] * (len(col_names)-1)
                value_entry = ['Value'] + ['0'] * (len(col_names)-1)
                value2_entry = ['--'] + ['0'] * (len(col_names)-1)
#                 printNodeTable(entry1=currtime.strftime("%d %H:%M:%S"),entry2=currtime.strftime("%d %H:%M:%S"),\
#                                entry3=currtime.strftime("%d %H:%M:%S"),entry4=currtime.strftime("%d %H:%M:%S"),\
#                                entry5=currtime.strftime("%d %H:%M:%S"),entry6=currtime.strftime("%d %H:%M:%S"),\
#                                entry7=currtime.strftime("%d %H:%M:%S"),entry8=currtime.strftime("%d %H:%M:%S"),offset=(printOffset+4))
#                 #printNodeTable(entry1='{:^10}'.format(''),entry2='{:^10}'.format(''),entry3='{:^10}'.format(''),\
                #               entry4='{:^10}'.format(''),entry5='{:^10}'.format(''),entry6='{:^10}'.format(''),\
                #               entry7='{:^10}'.format(''),entry8='{:^10}'.format(''),offset=printOffset+6)
                #printNodeTable(entry1='{:^10}'.format(''),entry2='{:^10}'.format(''),entry3='{:^10}'.format(''),\
                #               entry4='{:^10}'.format(''),entry5='{:^10}'.format(''),entry6='{:^10}'.format(''),\
                #               entry7='{:^10}'.format(''),entry8='{:^10}'.format(''),offset=printOffset+8)
                with open(hbStatFileName, "a") as heartFile:
                    heartFile.write("{}, {} \n".format(datetime.now(),sensorStatus[0]))      
                                   
            elif sensorStatus[0] == sensorList[0]:
                time_entry[1] = currtime.strftime("%d %H:%M:%S")
                value_entry[1] = sensorStatus[1]
                
#                 printNodeTable(entry1=currtime.strftime("%d %H:%M:%S"),offset=printOffset+4)
#                 printNodeTable(entry1=sensorStatus[1],offset=printOffset+6)
#                 #,entry2='{:^13}'.format(''),entry3='{:^13}'.format(''),\
                #               entry4='{:^13}'.format(''),entry5='{:^13}'.format(''),entry6='{:^13}'.format(''),\
                #               entry7='{:^13}'.format(''),entry8='{:^13}'.format('')
                #printNodeTable(entry1='{:^13}'.format(''),entry2='{:^13}'.format(''),entry3='{:^13}'.format(''),\
                #               entry4='{:^13}'.format(''),entry5='{:^13}'.format(''),entry6='{:^13}'.format(''),\
                #               entry7='{:^13}'.format(''),entry8='{:^13}'.format(''),offset=printOffset+8)
                #printNodeTable(entry1=datetime.now(),offset=printOffset+2)
                #printNodeTable(entry1=sensorStatus[1],offset=printOffset+3)
                #printNodeTable(entry1='',offset=printOffset+4)
                with open(sensorFiles[0], "a") as heartFile:
                    heartFile.write("{}, {} \n".format(datetime.now(),sensorStatus[1]))                         
#                 print '\x1b[{};1H'.format(printOffset + 2)
#                 print row_format.format('Time', datetime.now(), '' * (len(sensorList)-1))
#                 print '\x1b[{};1H'.format(printOffset + 3)
#                 print row_format.format('Value', sensorStatus[1], '' * (len(sensorList)-1))
#                 print '\x1b[{};1H'.format(printOffset + 4)
#                 print row_format.format('--', '', '' * (len(sensorList)-1))
            elif sensorStatus[0] == sensorList[1]:
                time_entry[2] = currtime.strftime("%d %H:%M:%S")
                value_entry[2] = sensorStatus[1]
                value2_entry[2] = sensorStatus[2]
#                 printNodeTable(entry2=currtime.strftime("%d %H:%M:%S"),offset=printOffset+4)
#                 printNodeTable(entry2=sensorStatus[1],offset=printOffset+6)
#                 printNodeTable(entry2=sensorStatus[2],offset=printOffset+8)
                #printNodeTable(entry2=datetime.now(),offset=printOffset+2)
                #printNodeTable(entry2=sensorStatus[1],offset=printOffset+3)
                #printNodeTable(entry2=sensorStatus[2],offset=printOffset+4)
                with open(sensorFiles[1], "a") as heartFile:
                    heartFile.write("{}, {}, {} \n".format(datetime.now(),sensorStatus[1],sensorStatus[2]))                         
#                 print '\x1b[{};1H'.format(printOffset + 2)
#                 print row_format.format('Time', '', datetime.now(), '' * (len(sensorList)-2))
#                 print '\x1b[{};1H'.format(printOffset + 3)
#                 print row_format.format('Value', '', sensorStatus[1], '' * (len(sensorList)-2))
#                 print '\x1b[{};1H'.format(printOffset + 4)
#                 print row_format.format('--', '', sensorStatus[2], '' * (len(sensorList)-2))
            elif sensorStatus[0] == sensorList[2]:
                time_entry[3] = currtime.strftime("%d %H:%M:%S")
                value_entry[3] = sensorStatus[1]
                #value2_entry[3] = str(sensorStatus[2])
#                 printNodeTable(entry3=currtime.strftime("%d %H:%M:%S"),offset=printOffset+4)
#                 printNodeTable(entry3=sensorStatus[1],offset=printOffset+6)
#                 printNodeTable(entry1='{:^10}'.format(''),entry2='{:^10}'.format(''),entry3='{:^10}'.format(''),\
#                                entry4='{:^10}'.format(''),entry5='{:^10}'.format(''),entry6='{:^10}'.format(''),\
#                                entry7='{:^10}'.format(''),entry8='{:^10}'.format(''),offset=printOffset+8)
#                 #printNodeTable(entry3=datetime.now(),offset=printOffset+2)
                #printNodeTable(entry3=sensorStatus[1],offset=printOffset+3)
                #printNodeTable(entry3='',offset=printOffset+4)
                with open(sensorFiles[2], "a") as heartFile:
                    heartFile.write("{}, {} \n".format(datetime.now(),sensorStatus[1]))                         
#                 print '\x1b[{};1H'.format(printOffset + 2)
#                 print row_format.format('Time', ''*2, datetime.now(), '' * (len(sensorList)-3))
#                 print '\x1b[{};1H'.format(printOffset + 3)
#                 print row_format.format('Value', ''*2, sensorStatus[1], '' * (len(sensorList)-3))
#                 print '\x1b[{};1H'.format(printOffset + 4)
#                 print row_format.format('--', ''*2, '', '' * (len(sensorList)-3))
            elif sensorStatus[0] == sensorList[3]:
                time_entry[4] = currtime.strftime("%d %H:%M:%S")
                value_entry[4] = sensorStatus[1]
                #value2_entry[4] = str(sensorStatus[2])
#                 printNodeTable(entry4=currtime.strftime("%d %H:%M:%S"),offset=printOffset+4)
#                 printNodeTable(entry4=sensorStatus[1],offset=printOffset+6)
#                 printNodeTable(entry1='{:^10}'.format(''),entry2='{:^10}'.format(''),entry3='{:^13}'.format(''),\
#                                entry4='{:^10}'.format(''),entry5='{:^10}'.format(''),entry6='{:^13}'.format(''),\
#                                entry7='{:^10}'.format(''),entry8='{:^10}'.format(''),offset=printOffset+8)
#                 #printNodeTable(entry4=datetime.now(),offset=printOffset+2)
                #printNodeTable(entry4=sensorStatus[1],offset=printOffset+3)
                #printNodeTable(entry4='',offset=printOffset+4)
                with open(sensorFiles[3], "a") as heartFile:
                    heartFile.write("{}, {} \n".format(datetime.now(),sensorStatus[1]))                         
#                 print '\x1b[{};1H'.format(printOffset + 2)
#                 print row_format.format('Time', ''*3, datetime.now(), '' * (len(sensorList)-4))
#                 print '\x1b[{};1H'.format(printOffset + 3)
#                 print row_format.format('Value', ''*3, sensorStatus[1], '' * (len(sensorList)-4))
#                 print '\x1b[{};1H'.format(printOffset + 4)
#                 print row_format.format('--', ''*3, '', '' * (len(sensorList)-4))
            elif sensorStatus[0] == sensorList[4]:
                time_entry[5] = currtime.strftime("%d %H:%M:%S")
                value_entry[5] = sensorStatus[1]
                time_entry[6] = currtime.strftime("%d %H:%M:%S")
                value_entry[6] = sensorStatus[2]
                #value2_entry[2] = str(sensorStatus[2])
#                 printNodeTable(entry5=currtime.strftime("%d %H:%M:%S"),entry6=currtime.strftime("%d %H:%M:%S"),offset=printOffset+4)
#                 printNodeTable(entry5=sensorStatus[1],entry6=sensorStatus[2],offset=printOffset+6)
#                 printNodeTable(entry1='{:^13}'.format(''),entry2='{:^13}'.format(''),entry3='{:^13}'.format(''),\
#                                entry4='{:^13}'.format(''),entry5='{:^13}'.format(''),entry6='{:^13}'.format(''),\
#                                entry7='{:^13}'.format(''),entry8='{:^13}'.format(''),offset=printOffset+8)
#                 #printNodeTable(entry5=datetime.now(),entry6=datetime.now(),offset=printOffset+2)
                #printNodeTable(entry5=sensorStatus[1],entry6=sensorStatus[2],offset=printOffset+3)
                #printNodeTable(entry5='',entry6='',offset=printOffset+4)
                with open(sensorFiles[4], "a") as heartFile:
                    heartFile.write("{}, {}, {} \n".format(datetime.now(),sensorStatus[1],sensorStatus[2]))                                                
#                 print '\x1b[{};1H'.format(printOffset + 2)
#                 print row_format.format('Time', ''*4, datetime.now(), datetime.now(), '' * (len(sensorList)-6))
#                 print '\x1b[{};1H'.format(printOffset + 3)
#                 print row_format.format('Value', ''*4, sensorStatus[1], sensorStatus[2], '' * (len(sensorList)-6))
#                 print '\x1b[{};1H'.format(printOffset + 4)
#                 print row_format.format('--', ''*4, '', '', '' * (len(sensorList)-6))
            elif sensorStatus[0] == "Pixie":
                time_entry[7] = currtime.strftime("%d %H:%M:%S")
                value_entry[7] = str(sensorStatus[1])
                value2_entry[7] = str(sensorStatus[0])
#                 printNodeTable(entry7=currtime.strftime("%d %H:%M:%S"),offset=printOffset+4)
#                 printNodeTable(entry7=sensorStatus[1],offset=printOffset+6)
#                 printNodeTable(entry7=sensorStatus[0],offset=printOffset+8)
                #printNodeTable(entry7=datetime.now(),offset=printOffset+2)
                #printNodeTable(entry7=sensorStatus[1],offset=printOffset+3)
                #printNodeTable(entry7=sensorStatus[2],offset=printOffset+4)
                with open(sensorFiles[5], "a") as heartFile:
                    heartFile.write("Pixie, {}, {} \n".format(datetime.now(),sensorStatus[1]))                         
            elif sensorStatus[0] == "Memento":
                #mementoTime = datetime.strptime(sensorStatus[1],"%Y-%m-%d %H:%M:%S")
                mementoTime = datetime.fromtimestamp(int(sensorStatus[1]))
                time_entry[7] = currtime.strftime("%d %H:%M:%S")
                value_entry[7] = mementoTime.strftime("%d %H:%M:%S")
                value2_entry[7] = str(sensorStatus[0])
#                 printNodeTable(entry7=currtime.strftime("%d %H:%M:%S"),offset=printOffset+4)
#                 printNodeTable(entry7=sensorStatus[1],offset=printOffset+6)
#                 printNodeTable(entry7=sensorStatus[0],offset=printOffset+8)
                #printNodeTable(entry7=sensorStatus[1],offset=printOffset+3)
                #printNodeTable(entry7=sensorStatus[2],offset=printOffset+4)
                with open(sensorFiles[5], "a") as heartFile:
                    heartFile.write("Memento, {}, {}, {} \n".format(datetime.now(),sensorStatus[1],sensorStatus[2]))
                
                try:
                    uploadMemento(mementoToken=DeploymentToken, mementoTime=mementoTime)
                except:
                    print '\x1b[{};1H'.format(40)
                    print "Memento Upload Error!"
                    print DeploymentToken
                    print mementoTime        
            elif sensorStatus[0] == "Agitation":
                localAgiType = int(sensorStatus[1].rstrip())
                if localAgiType==0:
                    localAgiStatus = False
                    localAgiIndx = 0
                else:
                    localAgiStatus = True
                    localAgiIndx = 1
                    try:
                        uploadAgitation(agitationToken=DeploymentToken, agitationTime=datetime.now(), agitationType=int(localAgiType))
                    except:
                        print '\x1b[{};1H'.format(40)
                        print "Agitation Upload Error!"
                time_entry[8] = currtime.strftime("%d %H:%M:%S")
                value_entry[8] = str(localAgiType)
                value2_entry[8] = str(localAgiStatus)
                
                globalParams.agiStatus = localAgiStatus
                globalParams.agiType = localAgiType
                globalParams.agiIndx += localAgiIndx
#                 printNodeTable(entry8=currtime.strftime("%d %H:%M:%S"),offset=printOffset+4)
#                 printNodeTable(entry8=sensorStatus[1],offset=printOffset+6)
#                 printNodeTable(entry8=sensorStatus[2],offset=printOffset+8)
                
#                 printNodeTable(entry1='{:^13}'.format(''),entry2='{:^13}'.format(''),entry3='{:^13}'.format(''),\
#                                entry4='{:^13}'.format(''),entry5='{:^13}'.format(''),entry6='{:^13}'.format(''),\
#                                entry7='{:^13}'.format(''),entry8=datetime.now().strftime("%d %H:%M:%S"),offset=printOffset+4)
#                 printNodeTable(entry1='{:^13}'.format(''),entry2='{:^13}'.format(''),entry3='{:^13}'.format(''),\
#                                entry4='{:^13}'.format(''),entry5='{:^13}'.format(''),entry6='{:^13}'.format(''),\
#                                entry7='{:^13}'.format(''),entry8=sensorStatus[1],offset=printOffset+6)
#                 printNodeTable(entry1='{:^13}'.format(''),entry2='{:^13}'.format(''),entry3='{:^13}'.format(''),\
#                                entry4='{:^13}'.format(''),entry5='{:^13}'.format(''),entry6='{:^13}'.format(''),\
#                                entry7='{:^13}'.format(''),entry8=sensorStatus[2],offset=printOffset+8)
#                 #printNodeTable(entry7=datetime.now(),offset=printOffset+2)
                #printNodeTable(entry7=sensorStatus[1],offset=printOffset+3)
                #printNodeTable(entry7=sensorStatus[2],offset=printOffset+4)
                with open(sensorFiles[5], "a") as heartFile:
                    heartFile.write("Agitation, {}, {}, {} \n".format(datetime.now(),sensorStatus[1],sensorStatus[2]))
                #uploadMemento(mementoToken=DeploymentToken, mementoTime=sensorStatus[1])    
                                         
#                 print '\x1b[{};1H'.format(printOffset + 2)
#                 print row_format.format('Time', ''*6, datetime.now())
#                 print '\x1b[{};1H'.format(printOffset + 3)
#                 print row_format.format('Value', ''*6, sensorStatus[1])
#                 print '\x1b[{};1H'.format(printOffset + 4)
#                 print row_format.format('--', ''*6, sensorStatus[0])
            
          
            
#             
#             elif sensorStatus[1] == "light":    
#                 printRSstatus(line2 = 'Door:  {}  {}  {}  {}                   '.format(datetime.now(), sensorStatus[0], sensorStatus[3], sensorStatus[4]), offset = printOffset)
#                 printRSstatus(line3 = 'Temp:  {}  {}  {}                       '.format(datetime.now(), sensorStatus[0], sensorStatus[5]), offset = printOffset)
#                 with open(rHeartBeatFileName, "a") as heartFile:
#                     heartFile.write("{}, {}, -- , -- , -- , {}, {}, {} \n".format(datetime.now(), sensorStatus[5], sensorStatus[2], sensorStatus[3], sensorStatus[4]))      
#             
#             
#             
#             #if sensorStatus[1] == "Accelerometer":
#             #    printRSstatus(line1 = 'Accel: {}  {}  {}                       '.format(datetime.now(), sensorStatus[0]), offset = printOffset)
#             if sensorStatus[1] == "ADC":
#                 printRSstatus(line1 = 'Audio: {}  {}  {}                       '.format(datetime.now(), sensorStatus[0], sensorStatus[2]), offset = printOffset)
#                 printRSstatus(line2 = 'Door:  {}  {}  {}  {}                   '.format(datetime.now(), sensorStatus[0], sensorStatus[3], sensorStatus[4]), offset = printOffset)
#                 printRSstatus(line3 = 'Temp:  {}  {}  {}                       '.format(datetime.now(), sensorStatus[0], sensorStatus[5]), offset = printOffset)
#                 with open(rHeartBeatFileName, "a") as heartFile:
#                     heartFile.write("{}, {}, -- , -- , -- , {}, {}, {} \n".format(datetime.now(), sensorStatus[5], sensorStatus[2], sensorStatus[3], sensorStatus[4]))                    
#             elif sensorStatus[1] == "light":
#                 printRSstatus(line4 = 'Light: {}  {}  {}                       '.format(datetime.now(), sensorStatus[0], sensorStatus[2]), offset = printOffset)
#                 with open(rHeartBeatFileName, "a") as heartFile:
#                     heartFile.write("{}, -- , {}, -- , -- , -- , -- , -- \n".format(datetime.now(), sensorStatus[2]))                    
#             elif sensorStatus[1] == "weather":
#                 printRSstatus(line5 = 'Hum:   {}  {}  {}                       '.format(datetime.now(), sensorStatus[0], sensorStatus[2]), offset = printOffset)
#                 printRSstatus(line6 = 'Press:  {}  {}  {}                       '.format(datetime.now(), sensorStatus[0], sensorStatus[3]), offset = printOffset)
#                 with open(rHeartBeatFileName, "a") as heartFile:
#                     heartFile.write("{}, -- , -- , {}, {}, -- , -- , -- \n".format(datetime.now(), sensorStatus[2], sensorStatus[3]))                    
#             elif sensorStatus[0] == "starting":
#                 printRSstatus(line1 = 'Audio: {}  {}  {}                       '.format(datetime.now(), 000, 000), offset = printOffset)
#                 printRSstatus(line2 = 'Door:  {}  {}  {}  {}                   '.format(datetime.now(), 000, 000, 000), offset = printOffset)
#                 printRSstatus(line3 = 'Temp:  {}  {}  {}                       '.format(datetime.now(), 000, 000), offset = printOffset)
#                 printRSstatus(line4 = 'Light: {}  {}  {}                       '.format(datetime.now(), 000, 000), offset = printOffset)
#                 printRSstatus(line5 = 'Hum:   {}  {}  {}                       '.format(datetime.now(), 000, 000), offset = printOffset)
#                 printRSstatus(line6 = 'Pres:  {}  {}  {}                       '.format(datetime.now(), 000, 000), offset = printOffset)
#                 with open(rHeartBeatFileName, "a") as heartFile:
#                     heartFile.write("---------------- Started at: {} ----------------,\n".format(datetime.now()))
#                     #heartFile.write("Time, Temperature, Light, Humidity, Pressure, Audio, Door1, Door2\n")
#             elif sensorStatus[0] == "Connection":
#                 printRSstatus(line1 = 'Audio: {}  {}  {}                       '.format(datetime.now(), 000, 000), offset = printOffset)
#                 printRSstatus(line2 = 'Door:  {}  {}  {}  {}                   '.format(datetime.now(), 000, 000, 000), offset = printOffset)
#                 printRSstatus(line3 = 'Temp:  {}  {}  {}                       '.format(datetime.now(), 000, 000), offset = printOffset)
#                 printRSstatus(line4 = 'Light: {}  {}  {}                       '.format(datetime.now(), 000, 000), offset = printOffset)
#                 printRSstatus(line5 = 'Hum:   {}  {}  {}                       '.format(datetime.now(), 000, 000), offset = printOffset)
#                 printRSstatus(line6 = 'Pres:  {}  {}  {}                       '.format(datetime.now(), 000, 000), offset = printOffset)
#                 with open(rHeartBeatFileName, "a") as heartFile:
#                     heartFile.write("---------------- Connected at: {} ----------------,\n".format(datetime.now()))
#                     heartFile.write("Time, Temperature, Light, Humidity, Pressure, Audio, Door1, Door2\n")
#                     
#             #elif sensorStatus[1] == "Connected":
#             #    printRSstatus(line1 = 'Accel: {}  Connected                    '.format(datetime.now()), offset = printOffset)
#             #elif sensorStatus[1] == "Disconnected":
#             #    pass
                
#             else:
#                 print "error parsing RS status"
#                 print sensorStatus
                
            
            print '\x1b[{};1H'.format(printOffset + 4)
            print row_format.format(*time_entry)
    
            print '\x1b[{};1H'.format(printOffset + 6)
            print row_format.format(*value_entry)
            
            print '\x1b[{};1H'.format(printOffset + 8)
            print row_format.format(*value2_entry)
        ####################################
        # end of critial section
        lock.release() 
        
        # send back Shimmer IDs and Start Time
        # Shimmer IDs is only needed on first connect, and timestamp is only needed when the relay station starts a new file
        
        currentTime = datetime.now()
        
        configMsg = "{};{};{}".format( globalParams.agiIndx, globalParams.agiType, currentTime)
        connection.sendall("{:03}".format(len(configMsg)) + configMsg)
    
        with open(hbStatFileName, "a") as heartFile:
            heartFile.write(configMsg+"\n")      
    
        
        connection.close()
    
        
        #time.sleep(10)
        #except:
            #print "error updating relay station"

    
   
