"""
  FileName      [ cmdParser.py ]
  PacakageName  [ cmdManager ]
  Synopsis      [  ]
  Author        [ EdwardLeeMacau ]
  Reference     [  ]
"""

from abc import ABC, ABCMeta, abstractmethod
from enum import Enum

from . import utils
from .getch import getch

class CmdExecuteStatus(Enum):
    DONE  = 0
    QUIT  = 1
    ERROR = 2

class CmdOptionError(Enum):
    CMD_OPT_MISSING     = 0
    CMD_OPT_EXTRA       = 1
    CMD_OPT_ILLEGAL     = 2
    CMD_OPT_FOPEN_FAIL  = 3

class Command(ABC):
    @abstractmethod
    def __init__(self):
        self.name = ''
        self.numMatch = 0

    @abstractmethod
    def help(self):
        pass

    @abstractmethod
    def usage(self):
        pass

    @abstractmethod
    def execute(self, *args, **kwargs) -> CmdExecuteStatus:
        pass

    @abstractmethod
    def parseArgs(self, string) -> list:
        pass

    @abstractmethod
    def autofill(self, string):
        pass

class CmdMgr:
    _instance = None
    _isInit = False

    def __new__(cls, prompt: str):
        if (cls._instance is None):
            CmdMgr._instance = super().__new__(cls)
        return CmdMgr._instance

    def __init__(self, prompt: str):            
        if not self._isInit:
            self._isInit = True

            self.history = []
            self.maximum = 0
            self.current = 0
            self.buffer = ""
            self.cursor = 0

            self.tabcount = 0
            
            self.cmds = {}

        self.prompt = prompt

    ## PUBLIC FUNCTION

    def update(self, cmd) -> bool:
        key = cmd.name[:cmd.numMatch]
        if self._interpret(key) is None:
            self.cmds[cmd.name] = cmd
            return True
        return False

    def executeOneCmd(self) -> CmdExecuteStatus:
        self.tabcount = 0
        self.cursor = 0
        self.buffer = ''
        arguments = ''
        keyword = ''
        char = ''

        print(self.prompt, end=' ', flush=True)

        while True:
            char = getch()

            if (char == b'\x03'):
                raise KeyboardInterrupt
            elif (char == b'\r'):
                print()
                break
            elif (char == b'\t'):
                self.tabcount += 1
                cmdString = self.buffer.strip().split(' ', 1)
                arguments = cmdString[1] if len(cmdString) == 2 else ''
                keyword = cmdString[0]
                if arguments == '':
                    if self._uniqueMatch(keyword) and self.tabcount >= 2:
                        self._autofill(keyword)
                    elif not self._uniqueMatch(keyword) and self.tabcount >= 2:
                        self._showAvailableCmd(keyword)
                        self._reprintCmd()
                    elif self.tabcount >= 2:
                        self._showAvailableCmd(keyword)
                        self._reprintCmd()
                else:
                    cmd = self._interpret(keyword)
                    if cmd is not None: 
                        self._addChar(cmd.autofill(arguments))
            elif (char == b'\x08'):
                self._backscape()
            elif (char == b'\x00'):
                char = getch()
                if (char == b'H'):
                    self._up()
                elif (char == b'I'):
                    self._up(10)
                elif (char == b'P'):
                    self._down()
                elif (char == b'Q'):
                    self._down(10)
                elif (char == b'K'):
                    self._left()
                elif (char == b'M'):
                    self._right()
            else:
                self._addChar(char.decode('ascii'))

        if (self.buffer == ""): 
            return CmdExecuteStatus.DONE

        # Mark History
        self.buffer = self.buffer.strip()
        self.history.append(self.buffer)
        self.maximum += 1
        self.current = self.maximum

        # Split as command and arguments
        cmdString = self.buffer.split(' ', 1)
        arguments = cmdString[1] if len(cmdString) == 2 else ''
        keyword = cmdString[0]
        return self._executeCommand(keyword, arguments)

    ## PRIVATE FUNCTION

    def _backscape(self):
        if self.cursor <= 0: return
        
        self.buffer = self.buffer[:self.cursor - 1] + self.buffer[self.cursor:]
        self.cursor -= 1
        currentPos = self.cursor
        print('\b', end='', flush=True)
        self._moveCursor(len(self.buffer))
        print(' \b', end='', flush=True)
        self._moveCursor(currentPos)

    def _delete(self):
        if self.cursor == len(self.buffer): return

        self._moveCursor(self.cursor + 1)
        self._backscape()

    def _left(self):
        if self.cursor <= 0: return
        self._moveCursor(self.cursor - 1)

    def _right(self):
        if self.cursor >= len(self.buffer): return
        self._moveCursor(self.cursor + 1)

    def _up(self, num: int = 1):
        if self.current <= 0: return

        # Save the temporary string if need
        if (self.current == self.maximum):
            self.history.append(self.buffer.strip())

        self.current = max(self.current - num, 0)
        self._retriveHistory(self.current)

    def _down(self, num: int = 1):
        if self.current >= self.maximum: return

        self.current = min(self.current + num, self.maximum)
        self._retriveHistory(self.current)

        # Take out the temporary string if need
        if (self.current == self.maximum):
            self.history.pop(-1)

    def _executeCommand(self, keyword: str, arguments: str) -> CmdExecuteStatus:        
        try:
            cmd = self._interpret(keyword)
            if cmd is None: 
                print('Command: {} is not supported.'.format(keyword)) 
                return CmdExecuteStatus.ERROR

            args = cmd.parseArgs(arguments)
            return cmd.execute(*args)
        except KeyError:
            return CmdExecuteStatus.ERROR

    ## PRIVATE HELPER FUNCTION

    def _reprintCmd(self):
        currentPos = self.cursor

        print(self.prompt, self.buffer, end='', flush=True)
        self.cursor = len(self.buffer)
        self._moveCursor(currentPos)

    def _uniqueMatch(self, keyword) -> bool:
        get = None

        for key, value in self.cmds.items():
            if len(keyword) > len(key):
                continue

            if utils.myNStrCmp(keyword, key, len(keyword)):
                if get is None:
                    get = value
                else:
                    return False

        return (get is not None)

    def _showAvailableCmd(self, keyword):
        print()

        for idx, key in enumerate(self.cmds.keys()):
            if (idx % 5 == 0 and idx):
                print()

            if utils.myNStrCmp(keyword, key, len(keyword)):
                print('{:12s}'.format(key), end='', flush=True)

        print()

    def _autofill(self, keyword):
        for key in self.cmds.keys():
            if utils.myNStrCmp(keyword, key, len(keyword)): 
                self._addChar(key[len(keyword):])
                self._addChar(' ')
                break

    def _moveCursor(self, newPos: int):
        while (newPos > self.cursor):
            print(self.buffer[self.cursor], end='', flush=True)
            self.cursor += 1

        while (newPos < self.cursor):
            print('\b', end='', flush=True)
            self.cursor -= 1

    def _moveCursorToEnd(self):
        """ Wrapper of _moveCursor """
        self._moveCursor(len(self.buffer))

    def _moveCursorToBegin(self):
        """ Wrapper of _moveCursor """
        self._moveCursor(0)

    def _clearInput(self):
        self._moveCursorToBegin()
        while (self.cursor < len(self.buffer)):
            print(' ', end='', flush=True)
            self.cursor += 1 
        self._moveCursorToBegin()

        self.buffer = ''
        self.cursor = 0

    def _addChar(self, char: str):
        self.buffer = self.buffer[:self.cursor] + char + self.buffer[self.cursor:]
        self._moveCursor(self.cursor + len(char))

    def _retriveHistory(self, idx: int):
        self._clearInput()
        self.current = idx
        self.buffer = self.history[idx]
        self._moveCursorToEnd()

    def _interpret(self, string) -> Command:
        for key, value in self.cmds.items():
            if len(string) < value.numMatch:
                continue

            if len(string) > len(key):
                continue

            if utils.myNStrCmp(string, key, len(string)):
                return self.cmds[key]

        return None

cmdMgr = CmdMgr('')
