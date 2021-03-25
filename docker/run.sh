#!/usr/bin/env bash

# SIGTERM-handler
term_handler() {
  exit 0
}
trap term_handler SIGTERM

if [ ! -f /sentinel/dash.conf ]; then
  if [ -z "$RPCUSER" -o -z "$RPCPASSWORD" -o -z "$RPCPORT" ]; then
    echo "When no /sentinel/dash.conf is present, you must at least set RPCUSER, RPCPORT and RPCPASSWORD environment variables"
    exit 1
  fi

  echo "" > /sentinel/dash.conf
  if [ -n "$RPCUSER" ]; then
    echo "rpcuser=${RPCUSER}" >> /sentinel/dash.conf
  fi
  if [ -n "$RPCPASSWORD" ]; then
    echo "rpcpassword=${RPCPASSWORD}" >> /sentinel/dash.conf
  fi
  if [ -n "$RPCPORT" ]; then
    echo "rpcport=${RPCPORT}" >> /sentinel/dash.conf
  fi
fi

if [ ! -f /sentinel/sentinel.conf ]; then
  if [ -z "$RPCHOST" ]; then
    echo "When no /sentinel/sentinal.conf is present, you must at least set the RPCHOST environment variable"
    exit 1
  fi

  echo "dash_conf=/sentinel/dash.conf" > /sentinel/sentinel.conf
  if [ -n "$RPCHOST" ]; then
    echo "rpchost=${RPCHOST}" >> /sentinel/sentinel.conf
  fi
  if [ -n "$NETWORK" ]; then
    echo "network=${NETWORK}" >> /sentinel/sentinel.conf
  fi

  # If these variables are not present, we let sentinel handle default values (which will use sqlite)
  if [ -n "$DB_HOST" ]; then
    echo "db_host=${DB_HOST}" >> /sentinel/sentinel.conf
  fi
  if [ -n "$DB_PORT" ]; then
    echo "db_port=${DB_PORT}" >> /sentinel/sentinel.conf
  fi
  if [ -n "$DB_NAME" ]; then
    echo "db_name=${DB_NAME}" >> /sentinel/sentinel.conf
  fi
  if [ -n "$DB_USER" ]; then
    echo "db_user=${DB_USER}" >> /sentinel/sentinel.conf
  fi
  if [ -n "$DB_PASSWORD" ]; then
    echo "db_password=${DB_PASSWORD}" >> /sentinel/sentinel.conf
  fi
  if [ -n "$DB_CHARSET" ]; then
    echo "db_charset=${DB_CHARSET}" >> /sentinel/sentinel.conf
  fi
  if [ -n "$DB_DRIVER" ]; then
    echo "db_driver=${DB_DRIVER}" >> /sentinel/sentinel.conf
  fi
fi

while true; do
  python ./bin/sentinel.py
  sleep 1m
done
