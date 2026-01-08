from core.file import *
from core.shell import Command, Mollusk
from core.game import Player
from core.colors import color, bcolors
import os
import readline

p = None

def gameinit():
  global p
  os.system("cls" if os.name == "nt" else "clear")
  p = Player(input("Enter username: "))
  print(f"Welcome, {p}! Logging in...")
  

def gameloop():
  os.system("cls" if os.name == "nt" else "clear")
  p.shell.start()
  while p.shell.running:
    p.shell.prompt()
  os.system("cls" if os.name == "nt" else "clear")


def run(user:str="user", host:str="localhost", root=ROOT):
  
  current:File = ROOT
  current_path = current.tracePath()

  os.system("cls" if os.name == "nt" else "clear")

  while True:
    try:
      cmdstr = input(f"{color(f"{user}@{host}", bcolors.PROFILE)}:{color(current_path, bcolors.CWD)}$ ")
      cmd:Command = Mollusk.parse(cmdstr)
    except EOFError:
      break
    
    # manual/help
    if (cmd.exec in ("help", "man")) or ("help" in cmd.wflags) or ("?" in cmd.lflags):
      print("There is no help.")
    elif cmd.exec in ('exit', 'logout'):
      break

    # clear
    if cmd.exec in ("clear", "cls"):
      os.system("cls" if os.name == "nt" else "clear")
      
    # list directories
    elif cmd.exec in ("l", "ls"):
      recursive = "r" in cmd.lflags or "recursive" in cmd.wflags
      all = "a" in cmd.lflags or "all" in cmd.wflags
      if len(cmd.args) > 0:
        current.ls(recursive=recursive, all=all, path=cmd.args[0])
      else:
        current.ls(recursive=recursive, all=all)

    # change directory
    elif cmd.exec == "cd":
      if len(cmd.args) > 0:
        tgt = current.followPath(cmd.args[0], dirOnly=True)
        if tgt is not None:
          current = tgt
          current_path = current.tracePath()
      else:
        current = ROOT
        current_path = current.tracePath()
    
    # make directory
    elif cmd.exec == "mkdir":
      if len(cmd.args) > 0:
        current.mkdir(cmd.args[0])
      else:
        print("ERROR: Path not specified")
    
    # make file
    elif cmd.exec in ("touch", "mkfile"):
      if len(cmd.args) > 0:
        current.touch(cmd.args[0])
      else:
        print("ERROR: File not specified")

    # code
    elif cmd.exec in ("code", "nano", "vim"):
      if len(cmd.args) > 0:
        replace = "r" in cmd.lflags or "recursive" in cmd.wflags
        current.edit(cmd.args[0], replace)
      else:
        print("ERROR: File not specified")
    
    # view file
    elif cmd.exec in ("cat", "view", "read"):
      if len(cmd.args) > 0:
        current.read(cmd.args[0])
      else:
        print("ERROR: File not specified")
    
    elif cmd.exec == "save":
      exportFiles(ROOT)
    elif cmd.exec == "":
      continue
    else:
      print(f"ERROR: No command found with name \"{cmd.exec}\"")

  print("")
  exportFiles(ROOT)


if __name__ == "__main__":
  gameinit()
  gameloop()