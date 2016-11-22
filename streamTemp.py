from streamUtils import *
from parameters import *
from kernel_test import isOutlier
from processTemp import lowPassFilter

# check if temperature data is ready
# return 0 if data read, 1 otherwise
def update_temp(connection, outFile, temp):
    # size of a temperature data packet is 20 bytes
    data = recv_nonblocking(connection, TEMP_PACKET_SIZE)
    if data != None:
        # if the file is empty, this is the first data received and we need to write the start time
        outFile.seek(0,2)
        if (outFile.tell() == 0):
            outFile.write(str(datetime.now()) + '\n')
         
        #split_data = struct.unpack("fff", data)
        #outFile.write("{0},{1},{2}\n".format(split_data[0], split_data[1], split_data[2]))
           
        outFile.write(data)
        split_data = parse_temp(data)
        if split_data != None:
            append_fixed_size(temp, float(split_data), 200)
        
            outlierProb = isOutlier(lowPassFilter(temp), 20)
            if (outlierProb > 0.8):
                pass
                #print outlierProb
                
        return 0
    
    else:
        return 1
    

# parses values for timestamp, degree C, degree F from string in csv format
# for plotting we only care about the degree F because the time axis is in samples                 
def parse_temp(raw_data):
    split_data = raw_data.split(",")
    try:
        # if degree F cannot be case to a float, the line is not data
        data = float(split_data[2])
    except:
        data = None
        
    return data