#!/usr/bin/env python3
from .abstract_command import AbstractCommand

HOME_COMMAND_ID = 2


class HomeCommand(AbstractCommand):
  def __init__(self):
    super(AbstractCommand, self).__init__(HOME_COMMAND_ID)
