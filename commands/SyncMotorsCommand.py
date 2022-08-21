#!/usr/bin/env python3
import string

from bitstring import pack
from commands.AbstractCommand import AbstractCommand

SYNC_MOTORS_COMMAND_ID = 7


class SyncMotorsCommand(AbstractCommand):
  def __init__(self):
    super().__init__(SYNC_MOTORS_COMMAND_ID)

  def parseCommandParams(self, stream, command):
    value = int(command.strip(string.ascii_letters))
    stream.append(pack('uint:8', value))

  def parseResponse(self, response):
    return
