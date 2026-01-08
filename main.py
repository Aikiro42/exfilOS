from core.file import *
from core.shell import Command, Mollusk
from core.game import Player
from core.colors import color, bcolors
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import ANSI
import os

def gameinit():
  os.system("cls" if os.name == "nt" else "clear")
  pname = prompt(ANSI(color("Enter username: ", bcolors.INFO)))
  if pname == "": pname = "guest"
  p = Player(pname)
  print(color(f"Welcome, {pname}! Logging in...", bcolors.OK))
  Mollusk.loadbar()
  return p
  

def gameloop(p: Player):
  os.system("cls" if os.name == "nt" else "clear")
  p.shell.start()
  while p.shell.running:
    p.shell.prompt()
  os.system("cls" if os.name == "nt" else "clear")
  print("Logging out...")
  exportFiles(p.home.rootdir)
  os.system("cls" if os.name == "nt" else "clear")

if __name__ == "__main__":
  p = gameinit()
  gameloop(p)