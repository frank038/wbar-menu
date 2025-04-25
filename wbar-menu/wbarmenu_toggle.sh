#!/bin/bash

thisdir=$(dirname "$0")
cd $thisdir

if ! pgrep -f wbar-menu.py; then
    ./wbar-menu.sh &
fi

if wlrctl toplevel find title:wbarmenu-1 state:unminimized; then
    wlrctl toplevel minimize title:wbarmenu-1 state:unminimized
elif wlrctl toplevel find title:wbarmenu-1 state:minimized; then
    wlrctl toplevel focus title:wbarmenu-1 state:minimized
fi
