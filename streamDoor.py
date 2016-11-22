from streamUtils import *
from parameters import *

# check if door sensor data is ready
# return 0 if data read, 1 otherwise 
def update_door(connection, outFile, door1, door2):
    data = recv_nonblocking(connection, DOOR_PACKET_SIZE)
    if data != None:
        # if the file is empty, this is the first data received and we need to write the start time
        outFile.seek(0,2)
        if (outFile.tell() == 0):
            outFile.write(str(datetime.now()) + '\n')
         
        # write data as it is received, then parse for plotting
        outFile.write(data)
        split_data = parse_door_byte(data)
        if (split_data[0] != None) and (split_data[1] != None):
            # noise data is plotted over 1000 samples = 10 seconds
            append_fixed_size(door1, split_data[0], 1000)
            append_fixed_size(door2, split_data[1], 1000)
            
        return 0
    
    else:
        return 1

            
# parses values for timestamp, noise level from string in csv format
# for plotting we only care about the noise level because the time axis is in samples
# noise level is the sum of the amplitudes in volts(rails are +-0.9V) of 100 samples with a sampling rate of 10kHz
def parse_door(raw_data):
    return_data = []
    split_data = raw_data.split(",")
    try:
        # if noise level cannot be cast to a float, the line is not data
        return_data.append(float(split_data[1]))
        return_data.append(float(split_data[2]))
    except:
        return_data.append(None)
        return_data.append(None)
        
    return return_data

# parses door sensor data when it is transmitted as byte data
def parse_door_byte(raw_data):
    return_data = []
    try:
        # if noise level cannot be cast to a float, the line is not data
        (t, s1, s2) = struct.unpack("fff", raw_data[0:12])
    except:
        return (None, None)
        
    return (s1, s2)