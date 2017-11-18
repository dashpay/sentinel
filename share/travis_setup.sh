#!/bin/bash
set -evx

mkdir ~/.chaincoincore

# safety check
if [ ! -f ~/.chaincoincore/.chaincoin.conf ]; then
  cp share/chaincoin.conf.example ~/.chaincoincore/chaincoin.conf
fi
