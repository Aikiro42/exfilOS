
from core.file import *
from core.colors import color, bcolors
from core.host import Host
import readline
import curses

user:str = "user@PythonOS"
current:File = ROOT
current_path = current.tracePath()

class Command:
  def __init__(self, exec: str, args: list[str], lflags:str, wflags:list[str]):
    self.exec = exec
    self.args = args
    self.lflags = lflags
    self.wflags = wflags

class Mollusk:
  def __init__(self, user:str, host:Host) -> None:
    self.user = user
    self.home = host
    self.changeHost(host)
  
  def changeHost(self, host:Host|None):
    if host is None:
      self.host = self.home
    else:
      self.host = host
    self.cwd = self.host.rootdir

  def prompt(self, promptString:str=""):
    s = f"{self.user}@{self.host.name}$"
    if promptString != "":
      s = promptString
    self.parse(input(s))

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
      
    return Command(exe, args, lflags, wflags)
  
  def run(self, cmd: Command):
    # Runs the passed command
    if cmd.exec in ("ls", "l"): self.ls(cmd)
    elif cmd.exec == "cd": self.cd(cmd)
    elif cmd.exec == "": pass

  def ls(self, cmd: Command):
    if len(cmd.args) == 0:
      ...
    else:
      file:str = cmd.args[1]

  def cd(self, cmd: Command):
    if len(cmd.args) == 0:
      self.cwd = self.host.rootdir
    else:
      file:str = cmd.args[1]