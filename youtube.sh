#!/bin/bash
while :
do

  ffmpeg -f lavfi -i anullsrc -rtsp_transport tcp -i rtsp://localhost:8554/test -tune zerolatency -vcodec libx264 -t 12:00:00 -pix_fmt + -c:v copy -c:a aac -strict experimental -f flv rtmp://a.rtmp.youtube.com/live2/humf-cu2j-uq2e-2wt9-46yc 

done