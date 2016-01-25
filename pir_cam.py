#!/usr/local/bin/python
import RPi.GPIO as GPIO
import time
import picamera
import datetime
import os

def getFileName():
	return datetime.datetime.now().strftime("/home/pi/picam/%Y-%m-%d_%H.%M.%S.h264")

sensorPin = 7

GPIO.setmode(GPIO.BOARD)
GPIO.setup(sensorPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

prevState = False
currState = False

cam = picamera.PiCamera()
cam.resolution = (1296, 730)
cam.framerate = 25
#cam.exposure_mode = 'off'

while True:
	time.sleep(.1)
	prevState = currState
	currState = GPIO.input(sensorPin)
	if currState != prevState:
		print "GPIO pin {0} is {1}".format(sensorPin, "HIGH" if currState else "LOW")
		if currState:
			fileName = getFileName()
			#annotate video with text timestamp
			#cam.annotate_text = fileName
			#start recording
			cam.start_recording(fileName, format='h264', quality=23)
		else:
			#stop recording
			cam.stop_recording()
			#get filesize and if small (short clip) delete
			fileSize = os.path.getsize('%s' % fileName)
			if fileSize < 2000000:
				print 'Deleting %s because fileSize of %s less than 200K' % (fileName, fileSize)
				os.system('rm -f %s' % fileName)
			else:
				print 'Saving, Converting and Uploading %s as fileSize of %s greater than 200K' % (fileName, fileSize)
				#convert recordng
				os.system('MP4Box -add %s %s.mp4' % (fileName, fileName))
				#delete orignal h264 file
				os.system('rm -f %s' % fileName)
				#dropbox upload
				os.system('./dropbox_uploader.sh -q upload %s.mp4 /' % fileName)
				#delete converted mp4 file
                        	os.system('rm -f %s.mp4' % fileName)
