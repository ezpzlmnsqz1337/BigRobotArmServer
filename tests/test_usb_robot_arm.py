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


if __name__ == '__main__':
    unittest.main()