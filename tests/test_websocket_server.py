import json
import unittest
from typing import cast

import websocket_server
from job_manager import JobManager, JobPayload


class FakeClient:
    def __init__(self) -> None:
        self.sent_messages: list[str] = []
        self.address = ('127.0.0.1', 1337)
        self.data = ''

    def send_message(self, payload: str) -> None:
        self.sent_messages.append(payload)


class WebsocketServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.events: list[JobPayload] = []
        self.commands_run: list[str] = []
        self.original_job_manager = websocket_server.job_manager
        self.original_is_connected = websocket_server.usb_robot_arm.isConnected
        self.original_send_command = websocket_server.usb_robot_arm.sendCommand

        websocket_server.usb_robot_arm.isConnected = lambda: True

        def execute(command: str) -> str:
            self.commands_run.append(command)
            return f'OK {command}\nBigRobotArm::READY\n'

        websocket_server.usb_robot_arm.sendCommand = execute
        websocket_server.job_manager = JobManager(execute, self.events.append)

    def tearDown(self) -> None:
        websocket_server.job_manager = self.original_job_manager
        websocket_server.usb_robot_arm.isConnected = self.original_is_connected
        websocket_server.usb_robot_arm.sendCommand = self.original_send_command

    def test_submit_job_returns_job_status_and_executes_commands(self):
        client = self._make_client()

        websocket_server.SimpleEcho.handle_json_message(
            self._as_socket(client),
            {
                'type': 'submitJob',
                'job': {'name': 'Demo', 'commands': ['G0 B0 S0 E0 WR0 W0', 'G28']}
            }
        )

        self.assertEqual(len(client.sent_messages), 1)
        payload = json.loads(client.sent_messages[0])
        self.assertEqual(payload['type'], 'jobStatus')
        self.assertEqual(payload['job']['name'], 'Demo')

    def test_get_queue_status_returns_active_and_pending_jobs(self):
        blocking_client = self._make_client()
        release_first_job = websocket_server.threading.Event()

        def execute(command: str) -> str:
            self.commands_run.append(command)
            if command == 'G0 B0 S0 E0 WR0 W0':
                release_first_job.wait(timeout=1)
            return f'OK {command}\nBigRobotArm::READY\n'

        websocket_server.job_manager = JobManager(execute, self.events.append)

        websocket_server.SimpleEcho.handle_json_message(
            self._as_socket(blocking_client),
            {
                'type': 'submitJob',
                'job': {'name': 'First', 'commands': ['G0 B0 S0 E0 WR0 W0']}
            }
        )
        websocket_server.SimpleEcho.handle_json_message(
            self._as_socket(blocking_client),
            {'type': 'submitJob', 'job': {'name': 'Second', 'commands': ['G28']}}
        )

        queue_client = self._make_client()
        websocket_server.SimpleEcho.handle_json_message(
            self._as_socket(queue_client),
            {'type': 'getQueueStatus'},
        )
        payload = json.loads(queue_client.sent_messages[-1])

        self.assertEqual(payload['type'], 'queueStatus')
        self.assertEqual(len(payload['jobs']), 2)
        self.assertEqual(payload['jobs'][0]['name'], 'First')
        self.assertEqual(payload['jobs'][1]['name'], 'Second')

        release_first_job.set()

    def test_cancel_job_requires_job_id(self):
        client = self._make_client()

        websocket_server.SimpleEcho.handle_json_message(
            self._as_socket(client),
            {'type': 'cancelJob'},
        )

        payload = json.loads(client.sent_messages[0])
        self.assertEqual(payload['type'], 'error')
        self.assertEqual(payload['message'], 'cancelJob requires a jobId')

    def test_submit_job_rejects_non_string_name(self):
        client = self._make_client()

        websocket_server.SimpleEcho.handle_json_message(
            self._as_socket(client),
            {
                'type': 'submitJob',
                'job': {'name': 123, 'commands': ['G28']},
            },
        )

        payload = json.loads(client.sent_messages[0])
        self.assertEqual(payload['type'], 'error')
        self.assertEqual(payload['message'], 'Job name must be a string')

    def test_raw_command_is_rejected_while_job_queue_is_open(self):
        client = self._make_client()
        release_first_job = websocket_server.threading.Event()

        def execute(command: str) -> str:
            self.commands_run.append(command)
            if command == 'G0 B0 S0 E0 WR0 W0':
                release_first_job.wait(timeout=1)
            return f'OK {command}\nBigRobotArm::READY\n'

        websocket_server.job_manager = JobManager(execute, self.events.append)
        websocket_server.SimpleEcho.handle_json_message(
            self._as_socket(client),
            {
                'type': 'submitJob',
                'job': {'name': 'First', 'commands': ['G0 B0 S0 E0 WR0 W0']},
            },
        )

        raw_client = self._make_client()
        raw_client.data = 'M503\n'

        websocket_server.SimpleEcho.handle(self._as_socket(raw_client))

        self.assertEqual(raw_client.sent_messages[-1], 'ERROR: Job in progress\n')
        release_first_job.set()

    def _make_client(self) -> FakeClient:
        return FakeClient()

    def _as_socket(self, client: FakeClient) -> websocket_server.SimpleEcho:
        return cast(websocket_server.SimpleEcho, client)