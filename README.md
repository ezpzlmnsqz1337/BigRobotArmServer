## BigRobotArmServer
Webserver and WebSocket server to host BigRobotArmUI web page to control BigRobotArm from web browser over USB.

## Tooling

- Python dependencies are managed with `uv`.
- Install `uv` once, then run `uv sync` in this directory to create the local environment.

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