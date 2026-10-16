#!/bin/bash
# usage: mezz.sh ID  -> mezz/ID.mp4 1080x1920 30fps all-intra-ish
S=/tmp/claude-0/-home-user-content/a076afeb-a72e-5a9b-8eab-5652dc33f51a/scratchpad
ffmpeg -y -v error -t 26 -i $S/src/$1.mov -an -vf "fps=30,scale=1080:1920:flags=lanczos,format=yuv420p" -c:v libx264 -preset veryfast -crf 16 -g 15 $S/mezz/$1.mp4
