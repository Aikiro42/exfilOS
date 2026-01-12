from core.file import *
from core.shell import Command, Mollusk
from core.user import User
from core.colors import color, bcolors
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import ANSI
import os

def gameinit() -> User:

  Mollusk.clear()
  pname = prompt(ANSI(color("Enter username: ", bcolors.INFO)))
  if pname == "": pname = "guest"
  print(color(f"Welcome, {pname}! Logging in...", bcolors.OK))
  Mollusk.loadbar()
  return User(pname)

def gameloop(sh: Mollusk):
  Mollusk.clear()
  sh.start()
  while sh.running:
    sh.prompt()
  print(color("Logging out...", bcolors.INFO))
  sh.savegame(None, True)
  Mollusk.clear()

if __name__ == "__main__":
  try:
    p = gameinit()
    sh = Mollusk(p)
    gameloop(sh)
  except KeyboardInterrupt:
    Mollusk.clear()
    print(color("WARNING: exfilOS force-exited via Ctrl+C.", bcolors.WARNING))
    if sh.savegame(None, forceExit=True):
      print(color("Game saved successfully.", bcolors.OK))
    else:
      print(color("Game failed to save!", bcolors.ERROR))