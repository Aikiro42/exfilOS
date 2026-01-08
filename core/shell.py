
from core.file import *
from core.colors import color, bcolors
import readline

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
  def __init__(self, user:str="user") -> None:
    self.user = user
    self.running = False

  def run(self):
    self.running = True
    while self.running:
      ...

  def stop(self):
    self.running = False


def parse(cmd: str) -> Command:
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