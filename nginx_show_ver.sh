#!/bin/sh

# check if "fmt" is GNU fmt
fmt --version 2>/dev/null 1>/dev/null
if [ $? -eq 0 ]; then
  FMT_OPTS="-s" # GNU fmt
else
  FMT_OPTS="-d-" # non-GNU fmt
fi

if [ -n "$1" -a -f "$1" ]; then
  SRC="cat $1"
  shift
else 
  SRC="nginx -V 2>&1"
fi

eval "$SRC" | fmt $FMT_OPTS | egrep --color=always "nginx/[0-9\.]+( \(.*\))?|${1:+$1|}$"
