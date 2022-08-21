#!/usr/bin/env python3
from commands.AbstractCommand import AbstractCommand

STATUS_COMMAND_ID = 8


class StatusCommand(AbstractCommand):
  def __init__(self):
    super().__init__(STATUS_COMMAND_ID)
