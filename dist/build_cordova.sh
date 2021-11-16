#!/usr/bin/env bash
if [ "$1" = "" ]; then
    action="run"
else
    action=$1
fi

if [ "$2" = "" ]; then
    app="sss"
else
    app=$1
fi

if [ "$action" = "run" ] || [ "$action" = "build" ];  then
    script_path=`dirname "${BASH_SOURCE[0]}"`
    cd $script_path && ./build_cordova.py $action $app setUp && ./.build_cordova.sh && ./build_cordova.py $action $app tearDown
else
    script_path=`dirname "${BASH_SOURCE[0]}"`
    cd $script_path && cordova "$@"
fi
