#!/usr/bin/env python3
from commands.AbstractCommand import AbstractCommand

SYNC_MOTORS_COMMAND_ID = 7


class SyncMotorsCommand(AbstractCommand):
  def __init__(self) -> None:
    super().__init__(SYNC_MOTORS_COMMAND_ID)

  def parseResponse(self, response):
    return
