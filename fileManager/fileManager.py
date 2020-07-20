"""
  FileName      [ fileManager.py ]
  PacakageName  [ fileManager ]
  Synopsis      [  ]
  Author        [ EdwardLeeMacau ]
  Reference     [  ]
"""

import os
from cmdManager.cmd import Command, CmdExecuteStatus

class UpdateFileCommand(Command):
    def __init__(self):
        self.name = 'UPDATEfile'
        self.numMatch = 6

    def help(self):
        pass

    def usage(self):
        pass

    def execute(self, *args, **kwargs) -> CmdExecuteStatus:
        pass

    def parseArgs(self, string) -> list:
        pass

    def autofill(self, string):
        pass
