#!/bin/bash

python3 -m http.server -d /home/pi/workspace/BigRobotArmServer/www &
python3 /home/pi/workspace/BigRobotArmServer/src/__main__.py
