
from core.file import *
from core.colors import *
from core.host import Host
from core.user import User
from core.editor import TextEditor
from core.util import *

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.completion import WordCompleter

from random import randint
import math, os, time, re
import threading

class Command:
  def __init__(self, cmdlist: list[str], exec: str, argi: list[int], flagi:list[int], flag_aliases: dict | None = None):
    self.cmdlist = cmdlist
    self.exec = exec
    self.argi = argi
    self.flagi = flagi
    self.flag_alias = flag_aliases or {}

  @property
  def cmdstr(self) -> str:
    return " ".join(f'"{x}"' if " " in x else x for x in self.cmdlist)
  
  @property
  def args(self) -> tuple:
    return tuple(self.cmdlist[i] for i in self.argi)
  
  @property
  def flags(self) -> tuple:
    ret = set()
    for i in self.flagi:
      flag = self.cmdlist[i]
      
      if flag.startswith("--"):  # long flag
        ret.add(flag[2:])
      
      elif flag.startswith("-"):  # short flag
        for c in flag[1:]:
          ret.add(self.flag_alias.get(c, c))
    return tuple(ret)
  
  @staticmethod
  def tokenize(cmdstr: str) -> list[str] | None:
    # pattern = r'''
    #     ("[^"]*")         |   # double quotes
    #     ('[^']*')         |   # single quotes
    #     (`[^`]*`)         |   # backticks
    #     (\S+)                 # unquoted token
    # '''
    pattern = r'''
        "(.*?)"         |   # double quotes
        '(.*?)'         |   # single quotes
        `(.*?)`         |   # backticks
        (\S+)               # unquoted token
    '''

    tokens = []
    pos = 0

    for match in re.finditer(pattern, cmdstr, re.VERBOSE):
        if match.start() != pos and not cmdstr[pos:match.start()].isspace():
            # Found unmatched junk (likely mismatched quotes)
            return None

        pos = match.end()

        # One of the capture groups will contain the value
        token = next(g for g in match.groups() if g is not None)
        tokens.append(token)

    # If leftover non-space text exists, quotes were mismatched
    if pos != len(cmdstr) and not cmdstr[pos:].isspace():
        return None

    return tokens

  # Parses a string as a command
  # Considers quotation marks, variable flags
  @staticmethod
  def parse(cmdstr: str, flag_aliases: dict | None = None) -> Command | None:
    
    tokens = Command.tokenize(cmdstr)
    if tokens is None: return None

    argi = []
    flagi = []
    for i in range(1, len(tokens)):
      token = tokens[i]
      if re.fullmatch(r'(-|--)[a-zA-Z]+', token) is not None:
          flagi.append(i)
      else:
          argi.append(i)

    return Command(tokens, tokens[0], argi, flagi, flag_aliases=flag_aliases)

  def __str__(self):
    return self.cmdstr

class Mollusk:
  def __init__(self, user: User) -> None:
    self.timers = {}
    self.logs = []
    self.promptSession = PromptSession()
    self.running = False
    self.reloading = False
    self.login(user)

    self.aliases: Dict[str, str] = {}
    self.setAlias("help",     "man")
    self.setAlias("logout",   "quit", "exit")
    self.setAlias("cls",      "clear")
    self.setAlias("ls",       "l")
    self.setAlias("mkfile",   "touch")
    self.setAlias("ed",       "edit", "code", "vim", "nano")
    self.setAlias("read",     "cat", "view")
    self.setAlias("savegame", "backup", "save")
    self.setAlias("loadgame", "restart", "reload")
    self.setAlias("download", "dl", "wget", "curl")

    self.cwd = self.host.fs.root
  
  def setAlias(self, cmd: str, *aliases: str):
    for alias in aliases:
      self.aliases[alias] = cmd
    
  def login(self, user: User):
    self.user = user
    self.home = Host("localhost", 2**16)
    self.home.load(f"savedata/{user.name}/filesys.json")
    self.host = self.home
    self.isHome = True
  
  @property
  def cwdstr(self):
    return self.cwd.path

  def start(self):
    self.running = True

  def stop(self):
    self.running = False
  
  def changeHost(self, host:Host | None):
    if host is None:
      self.host = self.home
    else:
      self.host = host
  
  @property
  def promptString(self):
    return f"{color(f"{self.user.name}@{self.host.name}", bcolors.PROFILE)}:{color(self.cwd.path, bcolors.CWD)}$ "

  def prompt(self, promptString:str=""):
    s = self.promptString
    if promptString != "":
      s = promptString
    try:
      fileCompleter = WordCompleter([])  # FIXME:
      cmdstr = self.promptSession.prompt(ANSI(s), completer=fileCompleter)
      parsedcmd = Command.parse(cmdstr)
      if isinstance(parsedcmd, Command):
        self.run(parsedcmd)
    except EOFError:
      self.stop()

  def run(self, cmd: Command):
    try:
      eval(f"self.{self.aliases.get(cmd.exec, cmd.exec)}(cmd)")
    except Exception as e:
      print(f"Exception: {e}")
      print(f"ERROR: Cannot process command `{cmd}`")

  # COMMANDS

  def cls(self, cmd: Command | None): Mollusk.clear()
  
  def ls(self, cmd: Command):
    dirPath: str
    if len(cmd.args) == 0:
      dirPath = self.cwd.path
    else:
      dirPath = cmd.args[0]
    targetDir: Dir = self.host.fs.resolve(self.cwd, dirPath)
    if isinstance(targetDir, Dir):
      for f in targetDir.files:
        if isinstance(f, Dir):
          print(color(f.name + "/", bcolors.DIR))
        elif isinstance(f, Link):
          print(color(f.name, bcolors.LINK))
        else:
          print(f.name)
  
  def cd(self, cmd: Command):
    dirPath = cmd.args[0]
    print(dirPath)
    targetDir: Dir = self.host.fs.resolve(self.cwd, dirPath)
    if isinstance(targetDir, Dir):
      self.cwd = targetDir
  
  def mkdir(self, cmd: Command):
    dirPath = cmd.args[0]
    if not self.host.fs.mkdir(self.cwd, dirPath):
      print(f"ERROR: Cannot make dir `{dirPath}`")

  def mkfile(self, cmd: Command) -> File: ...
  def rm(self, cmd: Command): ...
  def mv(self, cmd: Command, remove_source:bool=True):...
  def cp(self, cmd: Command):...  
  def rename(self, cmd: Command):...
  
  def read(self, cmd: Command): ...
  def ed(self, cmd: Command): ...
  
  def df(self, cmd: Command | None): ...
  def size(self, cmd: Command): ...
  def cache(self, cmd: Command): ...
  def download(self, cmd: Command): ...
  
  def logout(self, cmd: Command): ...
  def savegame(self, cmd: Command, exiting:bool=False, forceExit:bool=False, savepath:str="") -> bool: ...
  def loadgame(self, cmd: Command, savepath:str=""): ...
    
      
  # SECTION: PROGRAMS

  def gen(self, cmd: Command):
    ...

  def startTimer(self, name:str, duration: int): ...
  def checkTimer(self, name:str): ...

  @staticmethod
  def clear():
    os.system("cls" if os.name == "nt" else "clear")
  
  @staticmethod
  def loadbar(duration=1, barlength=30, failChance:float=0, end=""):
    progress = 0
    filllen = 0
    maxProgress = 100
    if (randint(0, 100) / 100) < failChance:
        maxProgress = randint(0, 99)
    while progress < maxProgress:
      filllen = min(barlength, math.ceil(progress*barlength/100))
      print(color(f"\r[{'|' * filllen}{' ' * (barlength-filllen)}]{end}", bcolors.INFO), end="")
      progadd = randint(1, 5)
      progress += progadd
      time.sleep(duration*progadd/100)
    else:
      print(color(f"\r[{'|' * barlength}]{end}", bcolors.OK if maxProgress == 100 else bcolors.ERROR), end="")
    print()
    return maxProgress == 100