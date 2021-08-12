#!/usr/bin/env python3
from bitstring import BitStream

from commands.AccelerationCommand import AccelerationCommand
from commands.BeginCommand import BeginCommand
from commands.EndCommand import EndCommand
from commands.GripperCommand import GripperCommand
from commands.HomeCommand import HomeCommand
from commands.PositionCommand import PositionCommand
from commands.ResetPositionCommand import ResetPositionCommand
from commands.SpeedCommand import SpeedCommand
from commands.StatusCommand import StatusCommand
from commands.SyncMotorsCommand import SyncMotorsCommand


class CommandBuilder:
  def __init__(self):
    self.currentCommand = None

  def parseCommand(self, message):

    commandType = message[0:4]
    if 'G0' in commandType:
      self.currentCommand = PositionCommand()
    if 'G1' in commandType:
      self.currentCommand = GripperCommand()
    if 'G28' in commandType:
      self.currentCommand = HomeCommand()
    if 'G92' in commandType:
      self.currentCommand = ResetPositionCommand()
    if 'M203' in commandType:
      self.currentCommand = SpeedCommand()
    if 'M201' in commandType:
      self.currentCommand = AccelerationCommand()
    if 'S' == commandType[0]:
      self.currentCommand = SyncMotorsCommand()
    if 'M503' in commandType:
      self.currentCommand = StatusCommand()
    if 'BEGIN I' in message:
      self.currentCommand = BeginCommand()
    if 'END' in commandType:
      self.currentCommand = EndCommand()

    if self.currentCommand == None:
      return BitStream('0x00')  # invalid message
    return self.currentCommand.parseCommand(message)

  def parseResponse(self, message):
    if self.currentCommand == None:
      return BitStream('0x00')  # no command being processed

    result = self.currentCommand.parseResponse(message)
    # command processing ended
    self.currentCommand = None
    return result


# parseCommand('G0 B2000 S2500 E3000 WR3500 W4000')
# parseCommand('G1 E1 P100')
