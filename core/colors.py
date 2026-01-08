from .const import bcolors

def color(str:str, color:str):
    return f"{color}{str}{bcolors.ENDC}"