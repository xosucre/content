#!/bin/bash
S=/tmp/claude-0/-home-user-content/a076afeb-a72e-5a9b-8eab-5652dc33f51a/scratchpad
ffmpeg -y -v error -t 26 -i $S/src/$1.mov -an -vf "fps=30,scale=1920:1080:flags=lanczos,format=yuv420p" -c:v libx264 -preset veryfast -crf 17 -g 15 $S/mezz_h/$1.mp4
