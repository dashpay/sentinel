#!/bin/bash
set -evx

mkdir ~/.dashcore

# safety check
if [ ! -f ~/.dashcore/.dash.conf ]; then
  cp share/dash.conf.example ~/.dashcore/dash.conf
fi
