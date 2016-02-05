#!/usr/local/bin/python
import RPi.GPIO as GPIO
from TwitterAPI import TwitterAPI
import time
import picamera
import datetime
import os
import logging
import socket

socket.setdefaulttimeout(60)

logging.basicConfig(filename='/home/pi/picam/logfeeder',format='%(asctime)s %(message)s',level=logging.INFO)


def getFileName():
    return datetime.datetime.now().strftime('/home/pi/picam/%Y-%m-%d_%H.%M.%S.h264')

def twitterup(myfileName):
    VIDEO_FILENAME = '%s.mp4' % myfileName
    TWEET_TEXT = myfileName
    TWEET_TEXT = TWEET_TEXT.replace("/home/pi/picam/","")
    TWEET_TEXT = TWEET_TEXT.replace(".h264","")
    CONSUMER_KEY = '-'
    CONSUMER_SECRET = '-'
    ACCESS_TOKEN_KEY = '-'
    ACCESS_TOKEN_SECRET = '-'
    api = TwitterAPI(CONSUMER_KEY,
                 CONSUMER_SECRET,
                 ACCESS_TOKEN_KEY,
                 ACCESS_TOKEN_SECRET)
    #logging.info("Saving, Converting and Uploading %s as fileSize of %s greater than 2MB" % (fileName, fileSize))
    #convert recordng
    os.system('MP4Box -add %s %s.mp4' % (fileName, fileName))
    #delete orignal h264 file
    os.system('rm -f %s' % fileName)
    bytes_sent = 0
    total_bytes = os.path.getsize(VIDEO_FILENAME)
    file = open(VIDEO_FILENAME, 'rb')
    r = api.request('media/upload', {'command':'INIT', 'media_type':'video/mp4', 'total_bytes':total_bytes})
    check_status(r)
    media_id = r.json()['media_id']
    segment_id = 0
    while bytes_sent < total_bytes:
      chunk = file.read(4*1024*1024)
      r = api.request('media/upload', {'command':'APPEND', 'media_id':media_id, 'segment_index':segment_id}, {'media':chunk})
      check_status(r)
      segment_id = segment_id + 1
      bytes_sent = file.tell()
      #logging.info("[" + str(total_bytes) + "]", str(bytes_sent))
    r = api.request('media/upload', {'command':'FINALIZE', 'media_id':media_id})
    check_status(r)
    r = api.request('statuses/update', {'status':TWEET_TEXT, 'media_ids':media_id})
    check_status(r)


def check_status(r):
    if r.status_code < 200 or r.status_code > 299:
        logging.warning("Status %s" % r.status_code)
        logging.warning("text %s" % r.text)
        #sys.exit(0)
	return

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
        #logging.info("GPIO pin {0} is {1}".format(sensorPin, "HIGH" if currState else "LOW"))
        if currState:
            fileName = getFileName()
            #annotate video with text timestamp
            #cam.annotate_text = fileName
            #start recording
            cam.start_recording(fileName, format='h264', quality=23)
        else:
            #stop recording
            cam.stop_recording()
            #get filesize and if too small (short clip) or too large delete
            fileSize = os.path.getsize('%s' % fileName)
            if (fileSize < 5000000):
                #logging.info("Deleting %s because fileSize of %s less than 2MB or greater 15MB" % (fileName, fileSize))
                os.system('rm -f %s' % fileName)
            else:
		try:
                  twitterup(fileName)
		except socket.TimeoutError:
		  time.sleep(5)
		  twitterup(fileName)
          #all done remove mp4
		  #logging.info("all done removing %s" % fileName)
          os.system('rm -f %s.mp4' % fileName)