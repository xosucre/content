#!/bin/bash
# usage: dl.sh OFFSET < urls (one per line); saves src/pNNN.mov in request order
S=/tmp/claude-0/-home-user-content/a076afeb-a72e-5a9b-8eab-5652dc33f51a/scratchpad/src
i=$1
while read u; do n=$(printf "p%03d" $i); (curl -sS -L -o $S/$n.mov "$u" || echo fail $n) & i=$((i+1)); done
wait
