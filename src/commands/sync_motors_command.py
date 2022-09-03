#!/usr/bin/env python3
import string

from bitstring import pack
from .abstract_command import AbstractCommand

SYNC_MOTORS_COMMAND_ID = 7


class SyncMotorsCommand(AbstractCommand):
  def __init__(self):
    super().__init__(SYNC_MOTORS_COMMAND_ID, ['uint:8'])
