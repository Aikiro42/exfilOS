
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
import math, os, time
import threading

class Command:
  def __init__(self, cmdstr: str, exec: str, args: list[str], lflags:str, wflags:list[str]):
    self.cmdstr = cmdstr
    self.exec = exec
    self.args = args
    self.lflags = lflags
    self.wflags = wflags

  # Parses a string as a command
  # Considers quotation marks, variable flags
  @staticmethod
  def parse(cmdstr: str) -> Command:...

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

    self.cwd = self.host.home
  
  def setAlias(self, cmd: str, *aliases: str):
    for alias in aliases:
      self.aliases[alias] = cmd
    
  def login(self, user: User):
    self.user = user
    try:
      self.home = Host("localhost", File.fromJson(f"{self.user.savepath}/filesys.json"))
    except Exception as e:
      print(e)
      self.home = Host("localhost", File(ROOT_NAME, True, capacity=2**16))
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
      fileCompleter = WordCompleter(list(self.host.fs.cwd.data.keys()))
      cmdstr = self.promptSession.prompt(ANSI(s), completer=fileCompleter)
      self.run(Mollusk.parse(cmdstr))
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
  def ls(self, cmd: Command): ...
  def cd(self, cmd: Command): ...
  def mkdir(self, cmd: Command): ...
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

  @staticmethod
  def parse(cmd: str) -> Command:
    # Static function that parses a string into a command
    split = cmd.split(" ")
    args = []
    exe = ""
    lflags = ""
    wflags = []
    for arg in split:
      if len(arg) <= 0: continue
      if arg[:2] == "--":
        wflags += [arg[2:]]
      elif arg[0] == "-":
        for lflag in arg[1:]:
          if lflag in lflags: continue
          lflags += lflag
      elif exe == "":
        exe = arg
      else:
        args += [arg]
      
    return Command(cmd, exe, args, lflags, wflags)