#!/usr/bin/env python3
import string
from bitstring import BitStream, pack
from commands.abstract_command import AbstractCommand

SYNC_MOTORS_COMMAND_ID = 7


class SyncMotorsCommand(AbstractCommand):
  def __init__(self):
    super().__init__(SYNC_MOTORS_COMMAND_ID, ["uint:8"])

  def parse_web_message_params(self, stream: BitStream, command: str):
    value = int(command.strip("\r\n").strip(string.ascii_letters))
    stream.append(pack("uint:8", value))

  def parse_serial_response(self, response: bytes):
    data = response.splitlines()
    stream = BitStream(data[1])
    s = stream.read("uint:8")
    result = f"BigRobotArm::SYNC-MOTORS: {s}\n"

    result += super().parse_serial_response(response)
    return result
