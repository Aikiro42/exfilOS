
from core.file import *
from core.colors import color, bcolors
from core.host import Host
from random import randint
import readline, math, os, time
import threading

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
    self.timers = {}
    self.logs = []

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
  
  @property
  def promptString(self):
    return f"{color(f"{self.user}@{self.host.name}", bcolors.PROFILE)}:{color(self.cwdstr, bcolors.CWD)}$ "

  def prompt(self, promptString:str=""):
    s = self.promptString
    if promptString != "":
      s = promptString
    try:
      cmdstr = input(s)
      self.run(Mollusk.parse(cmdstr))
    except EOFError:
      self.stop()

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
      
    return Command(exe, args, lflags, wflags)
  
  def run(self, cmd: Command):
    # manual/help
    if (cmd.exec in ("help", "man")) or ("help" in cmd.wflags) or ("?" in cmd.lflags):
      print("There is no help.")

    # logout
    elif cmd.exec in ('quit', 'exit', 'logout'):
      Mollusk.loadbar()
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
    
    # save progress
    elif cmd.exec == "save":
      Mollusk.loadbar()
      exportFiles(self.home.rootdir)
      print(color("Saved successfully!", bcolors.CYAN))

    # timer
    elif cmd.exec == "timer":
      if len(cmd.args) <= 0:
        print("ERROR: No duration or timer name specified")
      else:
        duration = 0
        try:
          duration = int(cmd.args[0])
          self.startTimer("default", duration)
        except:
          if len(cmd.args) == 1:
            self.checkTimer(cmd.args[0])
          else:
            try:
              duration = int(cmd.args[1])
              self.startTimer(cmd.args[0], duration)
            except: print("ERROR: Invalid Duration")

    # blank
    elif cmd.exec == "":
      pass

    # unknown
    else:
      print(f"ERROR: No command found with name \"{cmd.exec}\"")

  def startTimer(self, name:str, duration: int):
    timerTime = self.timers.get(name, -1)
    if timerTime <= 0:
      def t():
        while self.timers[name] > 0:
          time.sleep(1)
          self.timers[name] -= 1
        print(color(f"{name}: Time's up!", bcolors.CYAN), end="")
      self.timers[name] = duration
      threading.Thread(target=t, daemon=True).start()
    else:
      print(f"ERROR: Timer {name} already running ({timerTime}s left)")

  def checkTimer(self, name:str):
    time_left = self.timers.get(name, -1)
    if time_left <= 0:
      del self.timers[name]
    print(f"{name}: {time_left} s")

  @staticmethod
  def loadbar(duration=1, barlength=30):
    progress = 0
    while progress < 100:
      filllen = min(barlength, math.floor(progress*barlength/100))
      print(f"\r[{'|' * filllen}{' ' * (barlength-filllen)}]", end="")
      progadd = randint(1, 5)
      progress += progadd
      time.sleep(duration*progadd/100)

    print()