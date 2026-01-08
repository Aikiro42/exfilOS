from .const import bcolors
from prompt_toolkit.formatted_text import ANSI

def color(str:str, color:str):
    return f"{color}{str}{bcolors.ENDC}"