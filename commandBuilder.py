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


def parseCommand(message):
  commandType = message[0:4]
  if 'G0' in commandType:
    return PositionCommand().parseCommand(message)
  if 'G1' in commandType:
    return GripperCommand().parseCommand(message)
  if 'G28' in commandType:
    return HomeCommand().parseCommand(message)
  if 'G92' in commandType:
    return ResetPositionCommand().parseCommand(message)
  if 'M203' in commandType:
    return SpeedCommand().parseCommand(message)
  if 'M201' in commandType:
    return AccelerationCommand().parseCommand(message)
  if 'S' == commandType[0]:
    return SyncMotorsCommand().parseCommand(message)
  if 'M503' in commandType:
    return StatusCommand().parseCommand(message)
  if 'BEGIN I' in message:
    return BeginCommand().parseCommand(message)
  if 'END' in commandType:
    return EndCommand().parseCommand(message)
  return BitStream('0x00')  # invalid message


parseCommand('G0 B2000 S2500 E3000 WR3500 W4000')
parseCommand('G1 E1 P100')
