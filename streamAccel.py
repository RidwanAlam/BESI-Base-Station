from parameters import *
from streamUtils import append_fixed_size, recv_nonblocking
from datetime import datetime
import struct



# check if accelerometer data is ready
# return 0 if data read, 1 otherwise
def update_accel(connection, outFile, t, x, y, z):
    # each accelerometer packet is 22 bytes long
    # check if 10 packets are ready
    
    data = recv_nonblocking(connection, 20 * (ACCEL_PACKET_SIZE), False)
    if data != None:
        # if the file is empty, this is the first data received and we need to write the start time
        outFile.seek(0,2)
        if (outFile.tell() == 0):
            outFile.write(str(datetime.now()) + '\n')
        
        # raw bytes can be used to reduce bandwidth required
        #split_data = struct.unpack("HHHH", data)
        #outFile.write("{0},{1},{2},{3}\n".format(split_data[0], split_data[1], split_data[2], split_data[3]))
        
        
        split_data = parse_accel_byte(data)
        # add data to arrays
        # this only plots the first packet from every group received, which downsamples
        if (split_data[0] != None):
            # t is now RSSI scaled to fit onto the same scale as accelerometer
            append_fixed_size(t, (split_data[4] + 30) * 100, 200)
            append_fixed_size(x, split_data[1], 200)
            append_fixed_size(y, split_data[2], 200)
            append_fixed_size(z, split_data[3], 200)


        try:
            #check for all 0s, which signals a lost connection
            if x[-1] == 0 and y[-1] == 0 and z[-1] == 0 and split_data[0] == 0:
                # write time so that the duration of connection loss can be determined, "~~" is used as a separator
                outFile.write(str(datetime.now()) + '~~')
        except:
            pass    
        
        # save received data
        # even if we received less than a full 4 packets, the output file will have all the data correctly formatted 
        outFile.write(data)
        
        return 0
    
    else:
        return 1
       

# parses values for timestamp, x-axis, y-axis, and z-axis from string in csv format            
def parse_accel(raw_data):
    index = 0
    data = []
    
    for element in raw_data.split(","):
        # if data cannot be cast as an int, it is something other than data
        try:
            (int(element))
        except:
            data.append(None)
        else:
            # format is <timestamp>,<x-axis>,<y-axis>,<z-axis>,<RSSI>\n
            if index == 0:
                # timestamp is the number of ticks of a 32768 Hz clock
                # sampling at 256 Hz means 128 ticks per sample
                data.append(int(element)/TICKS_PER_SAMPLE)
                index = 1             
            elif index == 1:
                data.append(int(element))
                index = 2
            elif index == 2:
                data.append(int(element))
                index = 3
            elif index == 3:
                data.append(int(element))
                index = 4
            else:
                data.append(int(element))
                index = 0
                    
    #else:
        #data.append(None)
     
    if index != 0:
        data[0] = None
        
    return data

# parses values for timestamp, x-axis, y-axis, and z-axis from byte data           
def parse_accel_byte(raw_data):

    data = []
    # if data[0] == None when returned, the parse failed
    data.append(None)
    
    try:
        # each value should be stored as a 16-bit int
        (t,x,y,z,r) = struct.unpack("HHHHh", raw_data[0:10]) 
        data[0] = (t/TICKS_PER_SAMPLE)
        data.append(x)
        data.append(y)
        data.append(z)
        data.append(r)
      
    except:
        data[0] = None
            
    return data