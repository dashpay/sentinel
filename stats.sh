#! /bin/bash


echo "select table_schema, table_name, table_rows from TABLES where table_schema = 'sentinel'\\g" | mysql -h 127.0.0.1 -As --table -pninja2 information_schema

