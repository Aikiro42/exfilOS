from .const import bcolors

def color(str:str, color:bcolors):
    return f"{color}{str}{bcolors.ENDC}"