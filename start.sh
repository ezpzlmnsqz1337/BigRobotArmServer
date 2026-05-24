#!/bin/bash

set -euo pipefail

sudo systemctl start bigrobotarm-http.service bigrobotarm-websocket.service
