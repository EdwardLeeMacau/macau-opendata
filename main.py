"""
  FileName      [ main.py ]
  PacakageName  [ cmdManager ]
  Synopsis      [ Main of the project ]
  Author        [ EdwardLeeMacau ]
  Reference     [  ]
"""

from cmdManager import cmdParser
from cmdManager.cmdParser import CmdExecuteStatus
from cmdManager.cmd import *

manager = cmdParser.CmdMgr("CmdMgr >")

def initCommonCmd() -> bool:
    status = True
    
    for cmd in (QuitCommand(), ExitCommand(), HelpCommand(), UsageCommand()):
        status = manager.update(cmd)

        if not status:
            print('Init Command {} Error'.format(cmd.name))
            break

    return status

def initCrawlCmd() -> bool:
    status = True
    
    for cmd in tuple():
        status = manager.update(cmd)

        if not status:
            print('Init Command {} Error'.format(cmd.name))
            break

    return status

def main():
    if (not initCommonCmd() or not initCrawlCmd()):
        return

    try:
        status = CmdExecuteStatus.DONE

        while (status != CmdExecuteStatus.QUIT):
            status = manager.executeOneCmd()
            print()
    
    except KeyboardInterrupt:
        exit()

    return

if __name__ == "__main__":
    main()