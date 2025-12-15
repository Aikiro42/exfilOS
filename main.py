from core.file import *
from core.colors import color, bcolors

user:str = "user@PythonOS"
current:File = ROOT
current_path = current.tracePath()

while True:
  cmd = input(f"{color(user, bcolors.OKYELLOW)}:{color(current_path, bcolors.OKMAGENTA)}$ ").split(" ")

  if cmd[0] in ('exit', 'logout'):
    exportFiles(ROOT)
    break
  elif cmd[0] == "help":
    print("There is no help.")
  
  elif cmd[0] == "ls":
    recursive = "-r" in cmd
    all = "-a" in cmd
    if len(cmd) > 1:
      current.ls(recursive=recursive, all=all, path=cmd[1], root=ROOT)
    else:
      current.ls(recursive=recursive, all=all)

  elif cmd[0] == "cd":
    if len(cmd) < 2:
      print("ERROR: Path not specified")
    else:
      current = current.followPath(cmd[1], ROOT)
      current_path = current.tracePath()
  
  elif cmd[0] == "mkdir":
    if len(cmd) < 2:
      print("ERROR: Path not specified")
    else:
      current.mkdir(cmd[1])
  
  elif cmd[0] in ("touch", "mkfile"):
    if len(cmd) < 2:
      print("ERROR: File not specified")
    else:
      current.touch(cmd[1])

  elif cmd[0] == "nano":
    if len(cmd) < 2:
      print("ERROR: File not specified")
    else:
      replace = "-r" in cmd
      current.nano(cmd[1], replace)
  
  elif cmd[0] == "cat":
    if len(cmd) < 2:
      print("ERROR: File not specified")
    else:
      current.cat(cmd[1])