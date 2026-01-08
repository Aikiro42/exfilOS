
from core.file import *
from core.colors import color, bcolors
from core.host import Host
import readline
import curses
import os

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
    self.running = False

  def start(self):
    self.running = True

  def stop(self):
    self.running = False
  
  def changeHost(self, host:Host | None):
    if host is None:
      self.host = self.home
    else:
      self.host = host
    self.cwd = self.host.rootdir
    self.cwdstr = self.cwd.name

  def prompt(self, promptString:str=""):
    s = f"{color(f"{self.user}@{self.host.name}", bcolors.PROFILE)}:{color(self.cwdstr, bcolors.CWD)}$ "
    if promptString != "":
      s = promptString
    self.run(Mollusk.parse(input(s)))

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
    # manual/help
    if (cmd.exec in ("help", "man")) or ("help" in cmd.wflags) or ("?" in cmd.lflags):
      print("There is no help.")
    elif cmd.exec in ('quit', 'exit', 'logout'):
      self.stop()

    # clear
    elif cmd.exec in ("clear", "cls"):
      os.system("cls" if os.name == "nt" else "clear")
      
    # list directories
    elif cmd.exec in ("l", "ls"):
      recursive = "r" in cmd.lflags or "recursive" in cmd.wflags
      all = "a" in cmd.lflags or "all" in cmd.wflags
      if len(cmd.args) > 0:
        self.cwd.ls(recursive=recursive, all=all, path=cmd.args[0])
      else:
        self.cwd.ls(recursive=recursive, all=all)

    # change directory
    elif cmd.exec == "cd":
      if len(cmd.args) > 0:
        tgt = self.cwd.followPath(cmd.args[0], dirOnly=True)
        if tgt is not None:
          self.cwd = tgt
          self.cwdstr = self.cwd.tracePath()
      else:
        self.cwd = self.host.rootdir
        self.cwdstr = self.cwd.name
    
    # make directory
    elif cmd.exec == "mkdir":
      if len(cmd.args) > 0:
        self.cwd.mkdir(cmd.args[0])
      else:
        print("ERROR: Path not specified")
    
    # make file
    elif cmd.exec in ("touch", "mkfile"):
      if len(cmd.args) > 0:
        self.cwd.touch(cmd.args[0])
      else:
        print("ERROR: File not specified")

    # code
    elif cmd.exec in ("edit", "code", "nano", "vim"):
      if len(cmd.args) > 0:
        self.cwd.edit(cmd.args[0])
      else:
        print("ERROR: File not specified")
    
    # view file
    elif cmd.exec in ("cat", "view", "read"):
      if len(cmd.args) > 0:
        self.cwd.read(cmd.args[0])
      else:
        print("ERROR: File not specified")
    
    elif cmd.exec == "save":
      exportFiles(ROOT)
    elif cmd.exec == "":
      pass
    else:
      print(f"ERROR: No command found with name \"{cmd.exec}\"")

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