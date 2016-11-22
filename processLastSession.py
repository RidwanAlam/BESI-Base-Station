# Performs some processing on sensor data files,saves the files, and plots the data 
# File name is the sensor ID + the date it was recorded

import os
import processSession


#raw data files are named based on the socket port used to get the data from the BBB
basePort = int(raw_input("Enter the relay station ID: "))

processSession.processSession(basePort)
    
    
    