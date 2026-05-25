import unittest
from unittest import mock

import usb_robot_arm


class UsbRobotArmTests(unittest.TestCase):
    def tearDown(self) -> None:
        usb_robot_arm.clearConnection()

    def test_connect_falls_back_to_secondary_port(self) -> None:
        fallback_serial = mock.Mock()
        fallback_serial.is_open = True

        with mock.patch.object(
            usb_robot_arm.serial,
            'Serial',
            side_effect=[usb_robot_arm.serial.SerialException('busy'), fallback_serial],
        ) as serial_ctor:
            connected = usb_robot_arm.connect()

        self.assertTrue(connected)
        self.assertIs(usb_robot_arm.usb, fallback_serial)
        self.assertEqual(
            serial_ctor.call_args_list,
            [
                mock.call(usb_robot_arm.USB_PORT, usb_robot_arm.BAUD_RATE, timeout=2),
                mock.call(
                    usb_robot_arm.USB_FALLBACK_PORT,
                    usb_robot_arm.BAUD_RATE,
                    timeout=2,
                ),
            ],
        )

    def test_send_command_collects_response_until_ready(self) -> None:
        fake_usb = mock.Mock()
        fake_usb.is_open = True
        fake_usb.readline.side_effect = [b'OK\n', b'BigRobotArm::READY\n']
        usb_robot_arm.usb = fake_usb

        with mock.patch.object(usb_robot_arm.time, 'sleep', return_value=None):
            response = usb_robot_arm.sendCommand('M503')

        fake_usb.write.assert_called_once_with(b'M503\r')
        self.assertEqual(response, 'OK\nBigRobotArm::READY\n')

    def test_send_command_clears_connection_after_serial_error(self) -> None:
        fake_usb = mock.Mock()
        fake_usb.is_open = True
        fake_usb.write.side_effect = usb_robot_arm.serial.SerialException('lost')
        usb_robot_arm.usb = fake_usb

        with self.assertRaises(usb_robot_arm.ConnectionLostError):
            usb_robot_arm.sendCommand('M503')

        self.assertIsNone(usb_robot_arm.usb)

    def test_send_buffered_job_retries_when_firmware_queue_is_full(self) -> None:
        fake_usb = mock.Mock()
        fake_usb.is_open = True
        fake_usb.readline.side_effect = [
            b'BigRobotArm::QUEUED-TO\n',
            b'BigRobotArm::READY\n',
            b'BigRobotArm::QUEUE-FULL\n',
            b'BigRobotArm::READY\n',
            b'BigRobotArm::QUEUED-TO\n',
            b'BigRobotArm::READY\n',
            b'BigRobotArm::QUEUE-DRAINED\n',
            b'BigRobotArm::READY\n',
        ]
        usb_robot_arm.usb = fake_usb
        responses: list[str] = []

        with mock.patch.object(usb_robot_arm.time, 'sleep', return_value=None):
            usb_robot_arm.sendBufferedJob(
                ['G0 B0 S0 E0 WR0 W0', 'G0 B1 S1 E1 WR1 W1'],
                responses.append,
                lambda: False,
            )

        self.assertEqual(
            fake_usb.write.call_args_list,
            [
                mock.call(b'Q0 B0 S0 E0 WR0 W0\r'),
                mock.call(b'Q0 B1 S1 E1 WR1 W1\r'),
                mock.call(b'Q0 B1 S1 E1 WR1 W1\r'),
                mock.call(b'QFLUSH\r'),
            ],
        )
        self.assertEqual(len(responses), 2)


if __name__ == '__main__':
    unittest.main()