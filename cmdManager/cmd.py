"""
  FileName      [ cmd.py ]
  PacakageName  [ cmdManager ]
  Synopsis      [ common command for CLI tools ]
  Author        [ EdwardLeeMacau ]
  Reference     [  ]
"""

from .cmdParser import CmdExecuteStatus, CmdOptionError, Command, cmdMgr

class QuitCommand(Command):
    def __init__(self):
        self.name = 'Quit'
        self.numMatch = 1

    def help(self):
        print('    {:12s} Quit the process.'.format(self.name))
    
    def usage(self):
        print(self.name)

    def execute(self) -> CmdExecuteStatus:
        return CmdExecuteStatus.QUIT

    def parseArgs(self, string) -> list:
        return []

    def autofill(self, string) -> str:
        return ''

class ExitCommand(Command):
    def __init__(self):
        self.name = 'Exit'
        self.numMatch = 1

    def help(self):
        print('    {:12s} Exit the process.'.format(self.name))
    
    def usage(self):
        print(self.name)

    def execute(self) -> CmdExecuteStatus:
        return CmdExecuteStatus.QUIT

    def parseArgs(self, string) -> list:
        return []

    def autofill(self, string) -> str:
        return ''

class HelpCommand(Command):
    def __init__(self):
        self.name = 'Help'
        self.numMatch = 1
    
    def help(self, *args, **kwargs):
        print('    {:12s} Show the function of the command'.format(self.name))
    
    def usage(self, *args, **kwargs):
        print('{} [Command command]'.format(self.name))

    def execute(self, keyword='') -> CmdExecuteStatus:
        if (keyword == ''):
            for value in cmdMgr.cmds.values():
                value.help()
            return CmdExecuteStatus.DONE

        cmd = cmdMgr._interpret(keyword)
        if cmd is not None:
            cmd.help()
            return CmdExecuteStatus.DONE

        print('Command: {} is not supported.'.format(keyword)) 
        return CmdExecuteStatus.DONE

    def parseArgs(self, string) -> list:
        return [string]

    def autofill(self, string) -> str:
        return ''

class UsageCommand(Command):
    def __init__(self):
        self.name = 'USAge'
        self.numMatch = 3
    
    def help(self, *args, **kwargs):
        print('    {:12s} Show the usage of the command'.format(self.name))
    
    def usage(self, *args, **kwargs):
        print('{} <Command command>'.format(self.name))

    def execute(self, keyword='') -> CmdExecuteStatus:
        cmd = cmdMgr._interpret(keyword)
        if cmd is not None:
            cmd.help()
            return CmdExecuteStatus.DONE

        print('Command: {} is not supported.'.format(keyword)) 
        return CmdExecuteStatus.ERROR

    def parseArgs(self, string) -> list:
        return [string]

    def autofill(self, string) -> str:
        return ''
