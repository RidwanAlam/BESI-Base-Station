from streamUtils import *
from parameters import *

# parses values for timestamp, light level from string in csv format
# for plotting we only care about the light level because the time axis is in samples
def parse_light(raw_data):
    element = raw_data.split(",")
    try:
        # if light level cannot be case to a float, the line is not data
        data = (float(element[1]))
    except:
        data = None
            
    return data

# check if light data is ready
def update_light(connection, outFile, light):
    # each packet is 25 bytes
    data = recv_nonblocking(connection, LIGHT_PACKET_SIZE)
    if data != None:
        # if the file is empty, this is the first data received and we need to write the start time
        outFile.seek(0,2)
        if (outFile.tell() == 0):
            outFile.write(str(datetime.now()) + '\n')
            
        #split_data = struct.unpack("ff", data)
        #outFile.write("{0},{1}\n".format(split_data[0], split_data[1]))
        outFile.write(data)   
        split_data = parse_light(data)
        if split_data != None:
            append_fixed_size(light, float(split_data), 200)
            
        return 0
    else:
        return 1
