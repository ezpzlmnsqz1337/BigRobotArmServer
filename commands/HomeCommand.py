#!/usr/bin/env python3
from commands.AbstractCommand import AbstractCommand

HOME_COMMAND_ID = 2


class HomeCommand(AbstractCommand):
  def __init__(self) -> None:
    super().__init__(HOME_COMMAND_ID)
