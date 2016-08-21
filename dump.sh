#! /bin/bash

function run_query() {
    QUERY="$*"
    echo "$QUERY" | mysql -h 127.0.0.1 -As --table -pninja2 sentinel
}

QUERY="select * from event\\g"
run_query "$QUERY"

QUERY="select * from proposal\\G"
run_query "$QUERY"

QUERY="select * from governance_object\\G"
run_query "$QUERY"


