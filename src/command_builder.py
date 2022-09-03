#!/usr/bin/env python3
from bitstring import BitStream

from commands.acceleration_command import AccelerationCommand
from commands.begin_command import BeginCommand
from commands.end_command import EndCommand
from commands.gripper_command import GripperCommand
from commands.home_command import HomeCommand
from commands.position_command import PositionCommand
from commands.reset_position_command import ResetPositionCommand
from commands.speed_command import SpeedCommand
from commands.status_command import StatusCommand
from commands.sync_motors_command import SyncMotorsCommand


class CommandBuilder:
  def __init__(self):
    self.current_command = None

  def parse_web_message(self, message):

    command_type = message[0:4]
    if 'G0' in command_type:
      self.current_command = PositionCommand()
    if 'G1' in command_type:
      self.current_command = GripperCommand()
    if 'G28' in command_type:
      self.current_command = HomeCommand()
    if 'G92' in command_type:
      self.current_command = ResetPositionCommand()
    if 'M203' in command_type:
      self.current_command = SpeedCommand()
    if 'M201' in command_type:
      self.current_command = AccelerationCommand()
    if 'S' == command_type[0]:
      self.current_command = SyncMotorsCommand()
    if 'M503' in command_type:
      self.current_command = StatusCommand()
    if 'BEGIN I' in message:
      self.current_command = BeginCommand()
    if 'END' in command_type:
      self.current_command = EndCommand()

    if self.current_command == None:
      return BitStream('0x00').bytes  # invalid message
    return self.current_command.parse_web_message(message)

  def parse_serial_response(self, message):
    if self.current_command == None:
      return BitStream('0x00').bytes  # no command being processed

    result = self.current_command.parse_serial_response(message)
    # command processing ended
    self.current_command = None
    return result


# parse_command('G0 B2000 S2500 E3000 WR3500 W4000')
# parse_command('G1 E1 P100')
