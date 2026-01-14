from core.file import *

class Cache:
  def __init__(self, capacity: int):
    self.root = Dir('', capacity=capacity)
    self.cwd: Dir = self.root
    self._hostcwd_: Dir | None = None
  
  def switch(self, hostcwd: Dir) -> Dir:
    self._hostcwd_ = hostcwd
    return self.cwd
  
  def download(self, f: File) -> bool:
    return self.cwd.addFile(f, replace=True)