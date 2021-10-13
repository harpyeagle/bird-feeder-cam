# bird-feeder-cam

<img width="898" alt="bird-feeder" src="https://user-images.githubusercontent.com/16882283/137096818-f0beb0eb-67f4-4ebd-9caa-4cb3342e48b6.png">

Raspberry Pi, with Camera Module and PIR built into a bird feeder.

When the PIR is tripped (motion detected), the pi recordes a video. When the PIR returns to its orignal state (motion stops), the video is coverted into an mp4 and uploaded to dropbox.

#Dependencies
Picamera - https://picamera.readthedocs.org/en/release-1.10/

dropbox_uploader.sh - https://github.com/andreafabrizi/Dropbox-Uploader

