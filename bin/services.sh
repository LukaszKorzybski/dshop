#!/bin/bash

SPHINX="/usr/local"

function die() {
    echo $1
    exit 1
}

function start() {
    if pidof $SPHINX/bin/searchd 1>/dev/null
    then
        printf "Sphinx daemon is already running.\n"
    else
        printf "Starting Sphinx daemon..."
        /usr/local/bin/searchd  || die "Starting Sphinx daemon FAILED.\n"
    fi
}

function stop() {
    printf "Stopping Sphinx daemon...\n"
    /usr/local/bin/searchd --stop || die "Stopping Sphinx daemon FAILED.\n"
}

function status() {
    sphinx=`pidof $SPHINX/bin/searchd`
    if [[ $? == 0 ]]
    then
        printf "Sphinx daemon is running with pid $sphinx.\n"
    else
        printf "Sphinx daemon is NOT running.\n"
    fi
}

case $1 in
	'start')
    	start;;
    'stop')
        stop;;
    'restart')
    	stop
    	sleep 5
    	start;;
    'status')
        status;;
    *)
        echo "Usage: services start|stop|status";;
esac