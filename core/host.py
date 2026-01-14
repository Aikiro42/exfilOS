from core.file import File, Dir, FileSystem
from core.colors import color
from core.const import bcolors

class Host:
  def __init__(self, name:str, capacity=-1):
    self.name = name
    self.root = Dir('', capacity=capacity)
    self.root.addFile(Dir('mnt'), caller="Host.__init__")
    home = Dir('home')
    self.root.addFile(home, caller="Host.__init__")
    self.home = home

  def resolvePath(self, cwd: Dir, path: str) -> File | None:
    ...
  
  def resolveDir(self, cwd: Dir, path: str) -> tuple | None:
    ...
  
  def createDirectory(self, cwd: Dir, path: str) -> bool:
    tgt, name = self.resolveDir(cwd, path, dir=True)
    if tgt is not None:
      return tgt.addFile(Dir(name))

  def createFile(self, cwd: Dir, name: str) -> bool:
    return cwd.addFile(File(name))

  def removeDirectory(self, cwd: Dir, name: str, recursive: bool=False) -> File | None:
    return cwd.removeFile(name, recursive=recursive)



    