# this is the MAIN script

import multiprocessing
import multiprocessing.forking
import os
import sys
import socket
from parseConfig import parseConfig
from hbProcess import heartbeat_process
from colorama import init
#from statusMonitor import systemMonitor
import globalParams
    
# prevents the program from freezing when creating new processes
# Module multiprocessing is organized differently in Python 3.4+
try:
    # Python 3.4+
    if sys.platform.startswith('win'):
        import multiprocessing.popen_spawn_win32 as forking
    else:
        import multiprocessing.popen_fork as forking
except ImportError:
    import multiprocessing.forking as forking

if sys.platform.startswith('win'):
    # First define a modified version of Popen.
    class _Popen(forking.Popen):
        def __init__(self, *args, **kw):
            if hasattr(sys, 'frozen'):
                # We have to set original _MEIPASS2 value from sys._MEIPASS
                # to get --onefile mode working.
                os.putenv('_MEIPASS2', sys._MEIPASS) # @UndefinedVariable
                #os.putenv('_MEIPASS2', '')
            try:
                super(_Popen, self).__init__(*args, **kw)
            finally:
                if hasattr(sys, 'frozen'):
                    # On some platforms (e.g. AIX) 'os.unsetenv()' is not
                    # available. In those cases we cannot delete the variable
                    # but only set it to the empty string. The bootloader
                    # can handle this case.
                    if hasattr(os, 'unsetenv'):
                        os.unsetenv('_MEIPASS2')
                    else:
                        os.putenv('_MEIPASS2', '')

    # Second override 'Popen' class with our modified version.
    forking.Popen = _Popen

globalParams.init()

if __name__ == '__main__':
#if True:
    
    # required to prevent spawning multiple processes when run as an executable
    multiprocessing.freeze_support()
    
    heartbeatProcs = []
    # TODO: need to change if we want to use more than three Shimmers
    #ShimmerIDs = [None] * 3
    
      
    # get parameters from the config file  
    name, ports, useAccel, useLight, useADC, useWeather, numRelayStat, fileLengthSec, fileLengthDay, DeploymentID, DeploymentToken, networkNum = parseConfig()
    
    
    # print the host IP address so the user can enter it in the BBB application
    # If the basestation has 2 IP addresses, assume the second one is the local network that the BBB will connect to
    #try:
    #    name = socket.gethostbyname_ex(socket.gethostname())[-1][networkNum]
    #except:
    #    name = socket.gethostname()
    
    try:
        host = socket.gethostbyname(name)
        print "Basestation IP Address: ",host
    except socket.gaierror, err:
        print "cannot resolve hostname: ", name, err
        
    
               
    # Create a file structure to hold data for this deployment
    data_folder = "Data_Deployment_{}/".format(DeploymentID)
    if not os.path.exists(data_folder):
        os.mkdir(data_folder)
        
    
    
    # Create folders for each sensor
#     for relay_stat in ports:
#         relay_station_folder = data_folder + "Relay_Station_{}/".format(relay_stat)
#         if not os.path.exists(relay_station_folder):
#             os.mkdir(relay_station_folder)  
#         #if not os.path.exists(relay_station_folder + "Accelerometer"):
#         #    os.mkdir(relay_station_folder + "Accelerometer")
#         if not os.path.exists(relay_station_folder + "Temperature"):
#             os.mkdir(relay_station_folder + "Temperature")
#         if not os.path.exists(relay_station_folder + "Light"):
#             os.mkdir(relay_station_folder + "Light")
#         if not os.path.exists(relay_station_folder + "Audio"):
#             os.mkdir(relay_station_folder + "Audio")
#         if not os.path.exists(relay_station_folder + "Door"):
#             os.mkdir(relay_station_folder + "Door")
#         if not os.path.exists(relay_station_folder + "Humidity"):
#             os.mkdir(relay_station_folder + "Humidity")
#         if not os.path.exists(relay_station_folder + "Pressure"):
#             os.mkdir(relay_station_folder + "Pressure")
#         if not os.path.exists(relay_station_folder + "Pebble"):
#             os.mkdir(relay_station_folder + "Pebble")
#         if not os.path.exists(relay_station_folder + "Heartbeat"):
#             os.mkdir(relay_station_folder + "Heartbeat")
#         
    #print "Relay Station IDs: ",ports
    #print "Use Accelerometer: ",useAccel
    #print "Use Microphone and Temperature Sensor: ",useADC
    #print "Use Light Sensor", useLight
    
    # create a mutual exclusion lock so only one process prints at a time
    lock = multiprocessing.Lock()
    
    # create a queue for m=communication - currently not used
    comm_queue = multiprocessing.Queue()
    # Create a process for each BeagleBone
    try:
        for i in range(len(ports)): 
            # create a new process for each relay station
            # use a separate queue for communicating with each process
            heartbeatProcs.append(multiprocessing.Process(target = heartbeat_process, args=(comm_queue, ports[i], fileLengthSec, fileLengthDay, DeploymentID, DeploymentToken, networkNum, i, lock, host)))
    except:
        print "Error reading config file: incorrect parameters for relay stations"
    
    for proc in heartbeatProcs:  
        proc.start()
        
    #systemMonitor(comm_queue, numRelayStat)
   
    for proc in heartbeatProcs:  
        proc.join()
        
