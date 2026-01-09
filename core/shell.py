
from core.file import *
from core.colors import *
from core.host import Host
from random import randint
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import ANSI
import math, os, time
import threading

class Command:
  def __init__(self, exec: str, args: list[str], lflags:str, wflags:list[str]):
    self.exec = exec
    self.args = args
    self.lflags = lflags
    self.wflags = wflags

class Mollusk:
  def __init__(self, user:str, host:Host, cache:list[File]|None=None, cacheCap:int=16) -> None:
    self.user = user
    self.home = host
    self.changeHost(host)
    self.running = False
    self.timers = {}
    self.logs = []
    
    # Player data passed into the shell
    self.cache: list[File] = [] if cache is None else cache
    self.cacheCap = cacheCap

  def start(self):
    self.running = True

  def stop(self):
    self.running = False
  
  def changeHost(self, host:Host | None):
    if host is None:
      self.host = self.home
    else:
      self.host = host
    self.cwd = self.host.fs.cwd
    self.cwdstr = self.cwd.path
  
  @property
  def promptString(self):
    return f"{color(f"{self.user}@{self.host.name}", bcolors.PROFILE)}:{color(self.cwd.path, bcolors.CWD)}$ "

  def prompt(self, promptString:str=""):
    s = self.promptString
    if promptString != "":
      s = promptString
    try:
      cmdstr = prompt(ANSI(s))
      self.run(Mollusk.parse(cmdstr))
    except EOFError:
      self.stop()
  
  def run(self, cmd: Command):
    aliases = {
      "quit": "logout",
      "exit": "logout",

      "cls": "clear",
      
      "l": "ls",

      "touch": "mkfile",
      
      "code": "edit",
      "nano": "edit",
      "vim": "edit",

      "cat": "read",
      "view": "read",

      "backup": "savegame",
      "save": "savegame",

      "restart": "loadgame",
      "reload": "loadgame",

      "backpack": "viewCache",
      "cache": "viewCache",

      "dl": "download",
      "wget": "download",
      "curl": "download"

    }

    # manual/help
    if (cmd.exec in ("help", "man")) or ("help" in cmd.wflags) or ("?" in cmd.lflags):
      print("There is no help.")

    # logout
    elif cmd.exec in ('quit', 'exit', 'logout'):
      print(color("Logging out...", bcolors.INFO))
      Mollusk.loadbar()
      self.stop()

    # clear
    elif cmd.exec in ("clear", "cls"):
      self.clear()
      
    # list directories
    elif cmd.exec in ("l", "ls"):
      self.ls(cmd)

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
    elif cmd.exec in ("backup", "save", "savegame"):
      if Mollusk.loadbar(failChance=0.05):
        exportFiles(self.home.rootdir)
        print(color("Saved successfully!", bcolors.OK))
      else:
        print(color("Save Failed!", bcolors.ERROR))
    
    elif cmd.exec in ("restart", "reload", "loadgame"):
      print(color("RESTARTING GAME...", bcolors.WARNING))
      Mollusk.loadbar()
      self.clear()

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

    # view cache
    elif cmd.exec in ("backpack", "cache"):
      self.showCache()

    # download file to cache
    elif cmd.exec in ("dl", "download", "wget", "curl"):
      self.download(cmd)

    # blank
    elif cmd.exec == "": pass
    
    # unknown
    else:
      print(f"ERROR: No command found with name \"{cmd.exec}\"")

  # SECTION: TRAD BUILT-IN SHELL COMMANDS
  def clear(self):
    os.system("cls" if os.name == "nt" else "clear")
  
  def ls(self, cmd: Command):
    if not self.cwd.isDir:
      print(f"IMPOSSIBLE: Current working directory is a file")
      return
    
    tgt = self.cwd
    if len(cmd.args) > 0:
      path = cmd.args[0]
      tgt = self.cwd.followPath(path)
      if tgt is None:
        print(f"ERROR: Path {path} does not exist")
        return
      if not tgt.isDir:
        print(f"ERROR: Path {path} is not a directory")
        return
      
    all = 'a' in cmd.lflags or 'all' in cmd.wflags
    for filename, file in tgt.data.items(): # type: ignore
      if filename[0] == '.' and not all: continue  # skip hidden files
      print(f"{color(file.name, bcolors.DIR) if file.isDir else file.name}")

  # SECTION: PROGRAMS

  # timer <timer name (optional)> <timer duration in seconds>
  def startTimer(self, name:str, duration: int):
    timerTime = self.timers.get(name, -1)
    if timerTime <= 0:
      def t():
        while self.timers[name] > 0:
          time.sleep(1)
          self.timers[name] -= 1
        print(color(f"{name}: Time's up!", bcolors.INFO), end="")
      self.timers[name] = duration
      threading.Thread(target=t, daemon=True).start()
    else:
      print(f"ERROR: Timer {name} already running ({timerTime}s left)")

  # timer <running timer name>
  def checkTimer(self, name:str):
    time_left = self.timers.get(name, -1)
    if time_left <= 0:
      del self.timers[name]
    print(f"{name}: {time_left} s")

  # dl, download, wget, curl
  def download(self, cmd: Command):
    if len(cmd.args) <= 0:
      print("ERROR: File not specified")
      return
    
    if cmd.args[0] not in self.cwd.data.keys():
      print(f"ERROR: File {cmd.args[0]} not found")
      return
    if len(self.cache) >= self.cacheCap:
      print(f"ERROR: Cache full! Buy more RAM to increase it.")
      return

    obtained: File = self.cwd.getFile(cmd.args[0])
    
    if obtained.isDir:
      print("ERROR: File is directory; can only download files to Cache")
      return

    obtained.parent = None
    self.cache.append(self.cwd.getFile(cmd.args[0]))
    self.cwd.rm(cmd.args[0])

  # cache, backpack
  def showCache(self):
    cached = len(self.cache)
    print(color(f"Cache ({cached}/{self.cacheCap}): ", bcolors.INFO))
    if cached > 0:
      for i in range(cached):
        file = self.cache[i]
        print(f"[{i}]  {file.name}")

    else:
      print()
      print("Cache is empty.")
      print("To store files to cache, do")
      print()
      print("  download path/to/file.ext")
      print()

  @staticmethod
  def loadbar(duration=1, barlength=30, failChance:float=0):
    progress = 0
    filllen = 0
    maxProgress = 100
    if (randint(0, 100) / 100) < failChance:
        maxProgress = randint(0, 99)
    while progress < maxProgress:
      filllen = min(barlength, math.ceil(progress*barlength/100))
      print(color(f"\r[{'|' * filllen}{' ' * (barlength-filllen)}]", bcolors.INFO), end="")
      progadd = randint(1, 5)
      progress += progadd
      time.sleep(duration*progadd/100)
    else:
      print(color(f"\r[{'|' * barlength}]", bcolors.OK if maxProgress == 100 else bcolors.ERROR), end="")
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
      
    return Command(exe, args, lflags, wflags)