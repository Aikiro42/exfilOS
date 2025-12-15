from .const import bcolors

DIR_COLOR = bcolors.OKMAGENTA

def color(str:str, color:bcolors):
    return f"{color}{str}{bcolors.ENDC}"