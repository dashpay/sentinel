#!/bin/bash
set -evx

mkdir ~/.machinecoin

# safety check
if [ ! -f ~/.machinecoin/machinecoin.conf ]; then
  cp share/machinecoin.conf.example ~/.machinecoin/machinecoin.conf
fi
