#!/bin/bash

python3 -m http.server -d ./www &
python3 websocket-server.py &