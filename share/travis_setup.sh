#!/bin/bash
set -evx

mkdir ~/.bitgreen

# safety check
if [ ! -f ~/.bitgreen/.bitgreen.conf ]; then
  cp share/bitgreen.conf.example ~/.bitgreen/bitgreen.conf
fi
