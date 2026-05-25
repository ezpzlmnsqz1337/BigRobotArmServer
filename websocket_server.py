import json
import threading
from typing import Any

from simple_websocket_server import WebSocket, WebSocketServer

import usb_robot_arm
from job_manager import JobManager, JobQueueFullError

clients: set[WebSocket] = set()
clients_lock = threading.Lock()


def broadcast_json_event(event: dict[str, Any]) -> None:
    payload = json.dumps(event)
    stale_clients = []

    with clients_lock:
        for client in list(clients):
            try:
                client.send_message(payload)
            except Exception:
                stale_clients.append(client)

        for client in stale_clients:
            clients.discard(client)


job_manager = JobManager(usb_robot_arm.sendCommand, broadcast_json_event)


def make_error_event(message: str, job_id: str | None = None) -> dict[str, str]:
    event = {'type': 'error', 'message': message}
    if job_id is not None:
        event['jobId'] = job_id
    return event


def parse_json_message(raw_message: str) -> dict[str, Any] | None:
    stripped = raw_message.strip()
    if not stripped.startswith('{'):
        return None

    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        return None

    return payload if isinstance(payload, dict) else None


def _get_job_commands(job_data: dict[str, Any]) -> list[str]:
    commands = job_data.get('commands')
    has_non_string_command = isinstance(commands, list) and any(
        not isinstance(command, str) for command in commands
    )
    if not isinstance(commands, list) or has_non_string_command:
        raise ValueError('Job commands must be a non-empty array of command strings')
    return commands

class SimpleEcho(WebSocket):
    def handle(self) -> None:
        message = self.data.rstrip('\r').rstrip('\n')
        print(message)

        payload = parse_json_message(message)
        if payload is not None:
            self.handle_json_message(payload)
            return

        try:
            if usb_robot_arm.isConnected():
                if message == 'disconnect':
                    if job_manager.has_open_job_queue():
                        self.send_message(
                            'ERROR: Cannot disconnect while a job is running\n'
                        )
                        return
                    usb_robot_arm.disconnect()
                    self.send_message(getConnectionStatus())
                else:
                    if job_manager.has_open_job_queue():
                        self.send_message('ERROR: Job in progress\n')
                        return
                    response = usb_robot_arm.sendCommand(message)
                    self.send_message(response)
            else:
                if message == 'connect':
                    usb_robot_arm.connect()
                    self.send_message(getConnectionStatus())
        except usb_robot_arm.ConnectionLostError as error:
            self.send_message(f'{getConnectionStatus()}\nERROR: {error}')

    def handle_json_message(self, payload: dict[str, Any]) -> None:
        message_type = payload.get('type')

        if message_type == 'submitJob':
            if not usb_robot_arm.isConnected():
                self.send_message(
                    json.dumps(make_error_event('Controller not connected'))
                )
                return

            job_data = payload.get('job')
            if not isinstance(job_data, dict):
                self.send_message(json.dumps(make_error_event('Invalid job payload')))
                return

            commands = _get_job_commands(job_data)
            name = job_data.get('name')
            if name is not None and not isinstance(name, str):
                self.send_message(
                    json.dumps(make_error_event('Job name must be a string'))
                )
                return

            try:
                job = job_manager.submit_job(commands, name)
            except JobQueueFullError as error:
                self.send_message(json.dumps(make_error_event(str(error))))
                return
            except ValueError as error:
                self.send_message(json.dumps(make_error_event(str(error))))
                return

            self.send_message(json.dumps({'type': 'jobStatus', 'job': job}))
            return

        if message_type == 'getJobStatus':
            job_status = job_manager.get_job_status(payload.get('jobId'))
            self.send_message(json.dumps({'type': 'jobStatus', 'job': job_status}))
            return

        if message_type == 'getQueueStatus':
            self.send_message(
                json.dumps(
                    {'type': 'queueStatus', 'jobs': job_manager.get_queue_snapshot()}
                )
            )
            return

        if message_type == 'cancelJob':
            job_id = payload.get('jobId')
            if not isinstance(job_id, str):
                self.send_message(
                    json.dumps(make_error_event('cancelJob requires a jobId'))
                )
                return

            job_status = job_manager.cancel_job(job_id)
            if job_status is None:
                self.send_message(json.dumps(make_error_event('Job not found', job_id)))
                return

            self.send_message(json.dumps({'type': 'jobStatus', 'job': job_status}))
            return

        self.send_message(
            json.dumps(
                make_error_event(f'Unsupported message type: {message_type}')
            )
        )

    def connected(self) -> None:
        with clients_lock:
            clients.add(self)
        print(self.address, 'connected')
        self.send_message(getConnectionStatus())

    def handle_close(self) -> None:
        with clients_lock:
            clients.discard(self)
        print(self.address, 'closed')


def getConnectionStatus() -> str:
    status = 1 if usb_robot_arm.isConnected() else 0
    return f'connectionStatus:{status}'


def main() -> None:
    server = WebSocketServer('', 1337, SimpleEcho)
    server.serve_forever()


if __name__ == '__main__':
    main()