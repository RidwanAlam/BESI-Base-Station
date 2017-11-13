# functions used for BBB streaming application
import socket
import sys
# import pyqtgraph as pg
from datetime import datetime
from parameters import *
import struct
from colorama import init


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
      
