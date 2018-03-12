from datetime import datetime
from colorama import init
import time
import os
from colorama import init

from hbProcUtils import *

def notification_process(commQueue = None, PORT = 9999, 
	fileLengthSec = 600, fileLengthDay = 0, DeploymentID = 1, 
	DeploymentToken="1a79ee75e7328538f9df96bdc7e22f9d17ae398e", networkNum = 1, 
	ProcNum = 0, lock=None, host='191.168.0.100', notiTime=['17', '00']):

	# global agitationFlag

	relay_station_folder = "Data_Deployment_{0}/NotiManager/".format(DeploymentID)
	if not os.path.exists(relay_station_folder):
		os.mkdir(relay_station_folder) 
	notificationFileName = relay_station_folder + "notification_log.txt"
	with open(notificationFileName, "a") as notificationFile:
		notificationFile.write("timestamp, ACTION \n")
	
	col_names = ['--', 'Relay', 'NotiSent', 'Response', 'btnPush']
	row_format ='{:^13}' * len(col_names)
	printOffset = ProcNum*10 + 1 
	
	lock.acquire()
	
	init()
	print '\x1b[{};1H'.format(printOffset + 0)
	print '{:-^120}'.format('Notification Manager')
	
	print '\x1b[{};1H'.format(printOffset + 2)
	print row_format.format(*col_names)

	time_entry = ['Time'] + [''] * (len(col_names)-1)
	print '\x1b[{};1H'.format(printOffset + 4)
	print row_format.format(*time_entry)

	value_entry = ['Value'] + [''] * (len(col_names)-1)
	print '\x1b[{};1H'.format(printOffset + 6)
	print row_format.format(*value_entry)

	#test
	# print '\x1b[{};1H'.format(printOffset + 8)
	# print "notiTime = " + str(notiTime[0]) + ":" + str(notiTime[1]) 

	lock.release() 

	# initial values
	notiSTATE = "IDLE"
	notificationFlag = 0
	pebbleReceivedFlag = 0
	responseReceive = 0
	notiCount = 0
	endNotificationFlag = 0 #no more notification for the day

	NoNotiPeriod = [22,7]
	notiRepeatCount = 2#repeat notification "notiRepeatCount" times, if no btn response
	notiRepeatTime = 30 #minute, if no btn respose 

	while True:

		################ #State Transition ######################
		if notiSTATE == "IDLE": #no notification
			currTime = datetime.now()
			timeDELTA = (int(currTime.hour) - int(notiTime[0]))*60 + (int(currTime.minute) - int(notiTime[1]))
			if endNotificationFlag == 1:
				notiSTATE == "IDLE"
				if int(currTime.hour) < int(notiTime[0]): #resume notification when start a new day
					endNotificationFlag = 0 
					pebbleReceivedFlag = 0
					responseReceive = 0
					notificationFlag = 0
					notiCount = 0
					# print "NEW DAY - RESUME NOTIFICATION"
			elif (int(currTime.hour) >= NoNotiPeriod[0]) or (int(currTime.hour) <= NoNotiPeriod[1]): #late at night
				notiSTATE = "IDLE"
				pebbleReceivedFlag = 0
				responseReceive = 0
				notificationFlag = 0
				notiCount = 0
				endNotificationFlag = 1
			elif timeDELTA >= 0:
				notiSTATE = "Sending"
				pebbleReceivedFlag = 0
				responseReceive = 0
				notiCount = 0
					

			
		elif notiSTATE == "Sending": # sending notification
			if pebbleReceivedFlag == 1:
				notiSTATE = "NotiSENT"
				notificationFlag = 0
				notiSentTime = datetime.now()
			else:
				notificationFlag = 1
			
		elif notiSTATE == "NotiSENT": # notification sent
			if (responseReceive == 1) or (notiCount >= notiRepeatCount) or ( 
				(int(currTime.hour) >= NoNotiPeriod[0]) or (int(currTime.hour) <= NoNotiPeriod[1])): 
			#if received pebble resp || send notification > 3 times || late at night
				notiSTATE = "IDLE"
				pebbleReceivedFlag = 0
				responseReceive = 0
				notificationFlag = 0
				notiCount = 0
				endNotificationFlag = 1
			else:
				currTime = datetime.now()
				timeDELTA = currTime-notiSentTime
				if timeDELTA.seconds >= notiRepeatTime*60:
					notiSTATE = "Sending"
					pebbleReceivedFlag = 0
					responseReceive = 0
					notiCount += 1
			
		else:
			notiSTATE = "IDLE"
		################ #State Transition ######################


		try:
			connection = connectRecv(host, PORT, networkNum, None)
			connection.settimeout(5)
			relayMessage = connection.recv(1024).split(";")

			lock.acquire()
			currtime = datetime.now()

			if relayMessage[0] == "checkNoti":
				time_entry[1] = currtime.strftime("%d %H:%M:%S")
				if relayMessage[1] == "10039": 
					value_entry[1] = "r109"
				elif relayMessage[1] == "10044":
					value_entry[1] = "r110" 

				currentTime = datetime.now()

				#send notification
				configMsg = "{};{};{}".format( 0, notificationFlag, currentTime)
				connection.sendall("{:03}".format(len(configMsg)) + configMsg)

				with open(notificationFileName, "a") as notificationFile:
					notificationFile.write("{}, {} \n".format(datetime.now(),value_entry[1])) 


			elif relayMessage[0] == "sent2Pebble":
				time_entry[2] = currtime.strftime("%d %H:%M:%S")
				value_entry[2] = "last sent"

				currentTime = datetime.now()
				configMsg = "{};{};{}".format( 0, 0, currentTime)
				connection.sendall("{:03}".format(len(configMsg)) + configMsg)

				with open(notificationFileName, "a") as notificationFile:
					notificationFile.write("{}, {} \n".format(datetime.now(),"sent2Pebble")) 

				pebbleReceivedFlag = 1 #pebble received noti

			elif relayMessage[0] == "pebbleResp":
				time_entry[3] = currtime.strftime("%d %H:%M:%S")
				value_entry[3] = relayMessage[1]

				currentTime = datetime.now()
				configMsg = "{};{};{}".format( 0, 0, currentTime)
				connection.sendall("{:03}".format(len(configMsg)) + configMsg)

				with open(notificationFileName, "a") as notificationFile:
					notificationFile.write("{}, {} \n".format(datetime.now(),"pebbleResp")) 

				responseReceive = 1

			elif relayMessage[0] == "eventMark":
				time_entry[4] = currtime.strftime("%d %H:%M:%S")
				value_entry[4] = "eventMarked"

				currentTime = datetime.now()
				configMsg = "{};{};{}".format( 0, 0, currentTime)
				connection.sendall("{:03}".format(len(configMsg)) + configMsg) 

				with open(notificationFileName, "a") as notificationFile:
					notificationFile.write("{}, {} \n".format(datetime.now(),"eventMark")) 

			print '\x1b[{};1H'.format(printOffset + 4)
			print row_format.format(*time_entry)
	
			print '\x1b[{};1H'.format(printOffset + 6)
			print row_format.format(*value_entry)

			# #test
			# print '\x1b[{};1H'.format(printOffset + 8)
			# print "notiSTATE = " + notiSTATE

			lock.release()

			connection.close()
		except:
			pass
			# print "error in NotiManager"
			