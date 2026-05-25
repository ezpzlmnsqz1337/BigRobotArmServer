#!/bin/bash

set -euo pipefail

uv run pytest
uv run ruff check .
uv run mypy
uv run python -m py_compile job_manager.py usb_robot_arm.py websocket_server.py