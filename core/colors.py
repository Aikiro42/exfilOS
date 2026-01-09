from .const import bcolors
from prompt_toolkit.formatted_text import ANSI

def color(str:str, ansiColor:str):
    return f"{ansiColor}{str}{bcolors.ENDC}"

def printColor(*s, ansiColor="", sep=" ", end="\n", flush=False,file=None):
    print(*[color(str(ss), ansiColor) for ss in s], sep=sep, end=end, flush=flush, file=file)