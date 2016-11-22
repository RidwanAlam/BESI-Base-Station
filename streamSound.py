from streamUtils import *
from parameters import *

# check if sound data is ready
# return 0 if data read, 1 otherwise
def update_sound(connection, outFile, sound):
    # each packet is 23 bytes
    data = recv_nonblocking(connection, 5 * MIC_PACKET_SIZE)
    if data != None:
        # if the file is empty, this is the first data received and we need to write the start time
        outFile.seek(0,2)
        if (outFile.tell() == 0):
            outFile.write(str(datetime.now()) + '\n')
         
        #split_data = struct.unpack("ff", data)
        #outFile.write("{0},{1}\n".format(split_data[0], split_data[1]))   
        outFile.write(data)
        split_data = parse_sound_byte(data)
        if split_data != None:
            # noise data is plotted over 1000 samples = 10 seconds
            append_fixed_size(sound, split_data, 1000)
            
            # moving average - no longer used
            #to_avg = sound
            #if len(sound) > 100:
            #    to_avg = sound[len(sound) - 100:]
                
            #append_fixed_size(sound_sum, float(moving_avg(to_avg)), 1000)
            
        return 0
    
    else:
        return 1
            
# parses values for timestamp, noise level from string in csv format
# for plotting we only care about the noise level because the time axis is in samples
# noise level is the sum of the amplitudes in volts(rails are +-0.9V) of 100 samples with a sampling rate of 10kHz
def parse_sound(raw_data):
    split_data = raw_data.split(",")
    try:
        # if noise level cannot be cast to a float, the line is not data
        data = float(split_data[1])
    except:
        data = None
        
    return data

def parse_sound_byte(raw_data):
    try:
        # if noise level cannot be cast to a float, the line is not data
        (t,data) = struct.unpack("ff", raw_data[0:8])
    except:
        data = None
        
    return data