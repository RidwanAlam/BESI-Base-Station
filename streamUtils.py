# functions used for BBB streaming application
import socket
import sys
import pyqtgraph as pg
from datetime import datetime
from parameters import *
import struct

def printRSstatus(line1 = None, line2 = None, line3 = None, line4 = None, line5 = None, line6 = None, offset = 0):
    if line1 != None:
        print('\x1b[{};1H'.format(offset + 1))
        print(line1)
    
    if line2 != None:
        print('\x1b[{};1H'.format(offset + 2))
        print(line2)
        
    if line3 != None:
        print('\x1b[{};1H'.format(offset + 3))
        print(line3)
        
    if line4 != None:
        print('\x1b[{};1H'.format(offset + 4))
        print(line4)
        
    if line5 != None:
        print('\x1b[{};1H'.format(offset + 5))
        print(line5)
        
    if line6 != None:
        print('\x1b[{};1H'.format(offset + 6))
        print(line6)

# returns the average of value of data
def moving_avg(data):
    avg = 0
    if len(data) > 0:
        avg = float(sum(data))/len(data)
    return avg

# check connection for data up to BufSize in length and return it if present
def recv_nonblocking(connection, bufSize, accel=False):
    connection.settimeout(0)
    # send 1 byte to tell relay station that connection is still valid
    if not accel:
        try:
            connection.sendall("0")
        except:
            pass
        
    try:
        data = connection.recv(bufSize)
    except:
        data = None
    
     
    return data

# check connection for data up to BufSize in length and return it if present
# the first 4 bytes followed by a comma give the length of the payload
def recv_nonblocking_length(connection):
    connection.settimeout(0)
    try:
        header = connection.recv(2)
    except:
        return None
    # we got some data, so wait fort he rest  
    else:
        #print struct.unpack("H", header)
        try:
            #print "waiting for {} bytes of data".format(struct.unpack("H", header)[0])
            #connection.settimeout(1)
            # read until we get a comma
            while(len(header) != 2):
                header = header + connection.recv(2 - len(header))
            
            messageLen = struct.unpack("H", header)[0]
            #messageLen = int(header[:-1])c
            data = ''
            while(len(data) != messageLen):
                data = data + connection.recv(messageLen - len(data))
        
        except:
            print "E"
            return None
        
        else:
            #print "got remaining data"
            return data
    
    
    connection.settimeout(0)
    try:
        header = connection.recv(2)
    except:
        return None
    # we got some data, so wait fort he rest  
    else:
        #print struct.unpack("H", header)
        try:
            #print "waiting for {} bytes of data".format(struct.unpack("H", header)[0])
            #connection.settimeout(1)
            # read until we get a comma
            while(len(header) != 2):
                header = header + connection.recv(2 - len(header))
            
            messageLen = struct.unpack("H", header)[0]
            #messageLen = int(header[:-1])c
            
            data = connection.recv(messageLen)
        
        except:
            print "E"
            return None
        
        else:
            #print "got remaining data"
            if len(data) == messageLen:
                return data
            #else:
                #return None


# append new_data to array and remove the oldest piece of data from array if the length of array is greater than max_size 
def append_fixed_size(array, new_data, max_size):
    array.append(new_data)
    if len(array) > max_size:
            array.pop(0)
            

# listen at the given port for a connection, and return it if one is made. If no connection is made in timeout seconds, returns none
def connectRecv(host, port, networkNum, timeout):
    # configuration parameters; purpose unknown
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bind the socket to the port
    # if networkNum = 0, connect to relay stations on LAN, if networkNum = 1, connect on Wi-Fi
    #try:
    #    name = socket.gethostbyname_ex(socket.gethostname())[-1][networkNum]
    #except:
    #    name = socket.gethostbyname_ex(socket.gethostname())[-1][1-networkNum]
    name = socket.gethostbyname(host)
    server_address = (name, port)
    #print >>sys.stderr, 'starting up on %s port %s' % server_address
    sock.bind(server_address)
    
    sock.settimeout(timeout)
    # Listen for incoming connections
    sock.listen(1)
    
    
    # Wait for a connection
    #print >>sys.stderr, 'waiting for a connection'
    
    try:
        connection, client_address = sock.accept()
    except:
        return None
    
    #print >>sys.stderr, 'connection from', client_address
    # make connection nonblocking
    connection.settimeout(0)
    
    return connection
        
# initialize plots    
def init_plot(relayID):
    
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    
    curves = []
    win = pg.GraphicsWindow(title="Accelerometer data")
    win.resize(1000,600)
    win.setWindowTitle('Data from Relay Station {}'.format(relayID))
    
    # Enable antialiasing for prettier plots
    pg.setConfigOptions(antialias=True)
    
    # graph titles
    # TODO: add axis titles
    p1 = win.addPlot(title="Accelerometer")
    p1.setLabel('left', "Raw Accelerometer", units='')
    p1.setLabel('bottom', "samples (at 25.6 Hz)", units='')
    
    p2 = win.addPlot(title="Light")
    p2.setLabel('left', "Light Level", units='Lux')
    p2.setLabel('bottom', "samples (at 1 Hz)", units='')
    
    win.nextRow()
    p3 = win.addPlot(title="Noise")
    p3.setLabel('left', "Ambient Noise Level", units='')
    p3.setLabel('bottom', "Average Amplitude of 100 samples (sampled at 10 KHz)", units='')
    
    p4 = win.addPlot(title="Temperature")
    p4.setLabel('left', "Temperature", units='Degrees F')
    p4.setLabel('bottom', "samples (at 1 Hz)", units='')
    
    win.nextRow()
    p5 = win.addPlot(title="Door Sensor")
    p5.setLabel('left', "Motion Sensor Output", units='V')
    p5.setLabel('bottom', "Average Amplitude of 100 samples (sampled at 1 KHz)", units='')
    
    # ranges for each graph
    p1.setXRange(0, 200)
    p1.setYRange(0,4096)
    p2.setXRange(0, 200)
    p2.setYRange(0,1000)
    p3.setXRange(0, 1000)
    p3.setYRange(0,40)
    p4.setXRange(0, 200)
    p4.setYRange(30,100)
    p5.setXRange(0, 1000)
    p5.setYRange(0,100)
    
    
    
    # create a array of curve handlers to return
    curves.append(p1.plot(pen=(255,0,0), name="X-Axis"))
    curves.append(p1.plot(pen=(0,255,0), name="Y_Axis"))
    curves.append(p1.plot(pen=(0,0,255), name="Z_Axis"))
    curves.append(p1.plot(pen=(255,255,255), name="Timestamp"))
    
    curves.append(p2.plot(pen=(255,0,255), name="Lux"))
    
    curves.append(p3.plot(pen = (0, 255, 0), name="Noise"))
    curves.append(p3.plot(pen = (255, 0, 0), name="Noise_Avg"))
    curves.append(p4.plot(pen=(255,0,0), name="temperature"))
    
    curves.append(p5.plot(pen=(255,0,0), name="door sensor 1"))
    curves.append(p5.plot(pen=(0,0,255), name="door sensor 2"))
    
    return win, curves