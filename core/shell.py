
from core.file import *
from core.colors import *
from core.host import Host
from core.editor import TextEditor

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

  def __str__(self):
    return self.cmdstr

class Mollusk:
  def __init__(self, user:str, host:Host, cache:list[File]|None=None, cacheCap:int=16) -> None:
    self.user = user
    self.isHome = True
    self.home = host
    self.changeHost(host)
    self.timers = {}
    self.logs = []

    self.promptSession = PromptSession()

    self.running = False
    self.reloading = False
    
    # Player data passed into the shell
    self.cache: list[File] = [] if cache is None else cache
    self.cacheCap = cacheCap

  @property
  def cwd(self):
    return self.host.fs.cwd
  
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
    return f"{color(f"{self.user}@{self.host.name}", bcolors.PROFILE)}:{color(self.cwd.path, bcolors.CWD)}$ "

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
    aliases = {
      "man": "help",

      "quit": "logout",
      "exit": "logout",

      "clear": "cls",
      
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

    try:
      eval(f"self.{aliases.get(cmd.exec, cmd.exec)}(cmd)")
    except Exception as e:
      print(f"Exception: {e}")
      print(f"ERROR: Cannot process command `{cmd}`")


  # SECTION: TRAD BUILT-IN SHELL COMMANDS

  @staticmethod
  def clear():
    os.system("cls" if os.name == "nt" else "clear")
  
  def cls(self, cmd: Command | None):
    Mollusk.clear()
  
  def ls(self, cmd: Command):
    if not self.cwd.isDir:
      print(f"IMPOSSIBLE: Current working directory is a file")
      return
    
    isRecursive = 'r' in cmd.lflags or 'recursive' in cmd.wflags
    showAll = 'a' in cmd.lflags or 'all' in cmd.wflags
    if len(cmd.args) > 0:
      path = cmd.args[0]
      self.host.fs.ls(path, isRecursive, showAll)
    else:
      self.host.fs.ls("", isRecursive, showAll)
  
  def cd(self, cmd: Command):
    if len(cmd.args) <= 0:
      self.host.fs.cd('')
    else:
      self.host.fs.cd(cmd.args[0])
  
  def mkdir(self, cmd: Command):
    if len(cmd.args) <= 0:
      print("ERROR: No directory specified")
      return
    self.host.fs.mkdir(cmd.args[0])

  def mkfile(self, cmd: Command):
    if len(cmd.args) <= 0:
      print("ERROR: No filename specified")
      return
    self.host.fs.mkfile(cmd.args[0])

  def read(self, cmd: Command):

    if len(cmd.args) <= 0:
      print("ERROR: No filename specified")
      return
    
    toRead: File = self.host.fs.get(cmd.args[0], caller='read')
    
    if toRead.isDir:
      print(f"ERROR: Cannot read {cmd.args[0]}: '{toRead.name}' is directory")
      return
    
    print(toRead.data)
  
  def rm(self, cmd: Command):
    if len(cmd.args) <= 0:
      print("ERROR: No path specified")
      return
    self.host.fs.rm(cmd.args[0], 'r' in cmd.lflags or 'recursive' in cmd.wflags)
  
  def mv(self, cmd: Command, remove_source:bool=True):
    if len(cmd.args) <= 0:
      print("ERROR: No path specified")
      return
    if len(cmd.args) < 2:
      print("ERROR: No destination specified")
      return
    self.host.fs.mv(cmd.args[0], cmd.args[1], remove_source=remove_source)
  
  def cp(self, cmd: Command):
    self.host.fs.mv(cmd, remove_source=False)
  
  def rename(self, cmd: Command):
    if len(cmd.args) <= 0:
      print("ERROR: No path specified")
      return
    if len(cmd.args) < 2:
      print("ERROR: No file specified")
      return
    self.host.fs.rename(cmd.args[0], cmd.args[1])

  def viewCache(self, cmd: Command):
    ncache = len(self.cache)
    if ncache <= 0:
      print(color(f"No items in cache ({self.cacheCap} max capacity).", bcolors.INFO))
      return
    print(color(f"Cache (Capacity: {ncache}/{self.cacheCap}):", bcolors.INFO))
    for cachedFile in self.cache:
      print(f"- {cachedFile.name}")

  def ed(self, cmd: Command):
    if len(cmd.args) <= 0:
      print("ERROR: File not specified.")
    f: File | None = self.host.fs.get(cmd.args[0], 'ed')
    if f is None: return
    ed = TextEditor(f)
    ed.start()

  def chkdsk(self, cmd: Command):
    isVerbose = 'v' in cmd.lflags or 'verbose' in cmd.wflags
    self.host.fs.cwd.validateFiles(verbose = isVerbose)

  def logout(self, cmd: Command):
    if not self.isHome:
      print(f"ERROR: Cannot logout while not in host '{self.home.name}'")
    self.stop()

  def savegame(self, cmd: Command, exiting:bool=False, forceExit:bool=False) -> bool:
    
    # Cannot save away from home
    if not self.isHome:
      print(color(f"ERROR: Cannot save filesystem: not at home '{self.home.name}'", bcolors.ERROR))
      return False
    
    # Save game without loadboar on keyboard interrupt
    if forceExit:
      self.host.fs.root.toJson()
      return True
    
    # Loadbar on exit
    if exiting:
      Mollusk.loadbar(0.5)
      self.host.fs.root.toJson()
      return False
    
    # 10% chance to fail saving the system
    if not Mollusk.loadbar(0.5, failChance=0.1):
      print(color("ERROR: Failed to save filesystem!", bcolors.ERROR))
      return False
    
    files = self.host.fs.root.toJson()  # save success

    # Silent means "don't print success message"
    if 's' in cmd.lflags or 'silent' in cmd.wflags:
      return True
    
    print(color("Successfully saved filesystem!", bcolors.OK))
    
    # Verbose prints the contents of the saved json file.
    if 'v' in cmd.lflags or 'verbose' in cmd.wflags:
      print("[")
      for f in files:
        # print(f"  {f['index']}: {'{'}")
        print("  {")
        print(f'    "name": "{f["name"]}"')
        print(f'    "isDir": "{f["isDir"]}"')
        print(f'    "parent": {f["parent"]}')
        print("  }")
      print("]")

    return True
  
  def loadgame(self, cmd: Command):
    if not self.isHome:
      print(f"ERROR: Cannot load game: away from home '{self.home.name}'")
      return
    self.reloading = True
    
      
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

    obtained: File = self.host.fs.get(cmd.args[0], caller='download')
    
    if obtained.isDir:
      print("ERROR: File is directory; can only download files to Cache")
      return

    if self.host.fs.rm(cmd.args[0]):
      self.cache.append(obtained)

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
      
    return Command(cmd, exe, args, lflags, wflags)