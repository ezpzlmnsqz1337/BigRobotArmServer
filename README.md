## BigRobotArmServer
Webserver and WebSocket server to host BigRobotArmUI web page to control BigRobotArm from web browser over USB.

## Tooling

- Python dependencies are managed with `uv`.
- Install `uv` once, then run `uv sync` in this directory to create the local environment.
- Development tooling is installed with `uv sync --group dev`.
- The server currently keeps a flat module layout in the repo root. A `src/` migration is not required yet because the runtime and tests stay simple, and `pytest` now bootstraps the repo root explicitly via `tests/conftest.py`.

## Validate

- Run all server tests: `uv run pytest`
- Run linting: `uv run ruff check .`
- Run type checking: `uv run mypy`
- Install/update the local environment with dev tools: `uv sync --group dev`

## Run

- Development WebSocket server: `./start_dev.sh`
- Raspberry Pi service wrappers: `./start.sh` and `./stop.sh`
- Direct systemd units live in `systemd/`
- Direct validation: `uv run python -m py_compile usb_robot_arm.py websocket_server.py`

## Raspberry Pi deployment

- Define target settings in `deploy.env` using `deploy.env` as the template.
- Run `./deploy.sh` to sync the server project, run `uv sync --frozen` on the Pi, install the systemd units, and restart the services.
- The deploy flow intentionally leaves `www/` alone so UI deployment can remain a separate step.

## Dependencies

- `pyserial`
- `simple-websocket-server`

## Tests

- `tests/test_job_manager.py`: queue lifecycle and queue-capacity behavior.
- `tests/test_websocket_server.py`: JSON job routing, queue-status responses, and raw-command blocking while queued work is active.
- `tests/test_usb_robot_arm.py`: serial port fallback and command forwarding behavior.