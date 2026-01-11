from core.file import *
from core.shell import Command, Mollusk
from core.game import Player
from core.colors import color, bcolors
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import ANSI
import os

def gameinit():

  Mollusk.clear()
  p = Player("guest")
  return p

  pname = prompt(ANSI(color("Enter username: ", bcolors.INFO)))
  if pname == "": pname = "guest"
  print(color(f"Welcome, {pname}! Logging in...", bcolors.OK))
  Mollusk.loadbar()

def gameloop(p: Player):
  Mollusk.clear()
  p.shell.start()
  while p.shell.running:
    p.shell.prompt()
    if p.shell.reloading:
      Mollusk.loadbar()
      Mollusk.clear()
      p.load()
      p.shell.start()
  print(color("Logging out...", bcolors.INFO))
  p.shell.savegame(None, True)
  Mollusk.clear()

if __name__ == "__main__":
  try:
    p = gameinit()
    gameloop(p)
  except KeyboardInterrupt:
    Mollusk.clear()
    print(color("WARNING: exfilOS force-exited via Ctrl+C.", bcolors.WARNING))
    if p.shell.savegame(None, forceExit=True):
      print(color("Game saved successfully.", bcolors.OK))
    else:
      print(color("Game failed to save!", bcolors.ERROR))