#!/bin/sh
ARG=$1
SETUPARG=${ARG:="nosetup"}
CURPWD=$PWD
cd /home/james/games/Privateer//bin
sh vsinstall.sh $SETUPARG
