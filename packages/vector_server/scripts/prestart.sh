#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Uso: $0 <host> <port> <command>"
    exit 1
fi

host="$1"
port="$2"
command="$3"

echo "Waiting for connection to $host:$port"

while ! nc -z "$host" "$port"; do
    sleep 0.1
done

echo "$host:$port is available, running $command"

exec "$command"
