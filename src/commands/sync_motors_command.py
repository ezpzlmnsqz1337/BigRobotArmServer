#!/usr/bin/env python3
import string

from bitstring import pack
from .abstract_command import AbstractCommand

SYNC_MOTORS_COMMAND_ID = 7


class SyncMotorsCommand(AbstractCommand):
  def __init__(self):
    super(AbstractCommand, self).__init__(SYNC_MOTORS_COMMAND_ID)

  def parse_command_params(self, stream, command):
    value = int(command.strip(string.ascii_letters))
    stream.append(pack('uint:8', value))

  def parse_response(self, response):
    return
