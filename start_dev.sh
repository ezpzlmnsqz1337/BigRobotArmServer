#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_DIR="$SCRIPT_DIR/run"
WS_PID_FILE="$PID_DIR/websocket_server.pid"

mkdir -p "$PID_DIR"

cleanup() {
	rm -f "$WS_PID_FILE"
}

trap cleanup EXIT INT TERM

uv run python websocket_server.py &
echo "$!" > "$WS_PID_FILE"

wait "$(cat "$WS_PID_FILE")"