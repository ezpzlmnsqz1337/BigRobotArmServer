#!/usr/bin/env python3
from bitstring import BitStream
from commands.abstract_command import AbstractCommand

STATUS_COMMAND_ID = 8


class StatusCommand(AbstractCommand):
  def __init__(self):
    super().__init__(STATUS_COMMAND_ID)

  def parse_serial_response(self, response: bytes):
    data = response.splitlines()
    stream = BitStream(data[1])

    result = ""
    for type in ["POSITION", "ACCELERATION", "SPEED"]:
      b, s, e, wr, w, = self._parse_motor_values(stream)
      result += f"BigRobotArm::{type}: B{b} S{s} E{e} WR{wr} W{w}\n"

    g_enabled = stream.read("uint:8")
    g_position = stream.read("uint:8")
    sync_enabled = stream.read("uint:8")

    result += f"BigRobotArm::GRIPPER: E{g_enabled} P{g_position}\n"
    result += f"BigRobotArm::SYNC-MOTORS: {sync_enabled}\n"

    result += super().parse_serial_response(response)
    return result
