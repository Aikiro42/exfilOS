import json
from typing import Dict
from .const import *
from .colors import color
from copy import deepcopy
import secrets, string
from pathlib import Path

RESERVED_NAMES = [
  ROOT_NAME,
  "cache",
]

class File:
  def __init__(self, name:str, data="", parent:Dir|None=None):
    self.name: str = name
    self.parent: Dir | None = parent
    self._data_ = data

  @property
  def isDir(self): return False

  @property
  def data(self) -> str:
    return self._data_

  @data.setter
  def data(self, value: str):
    self._data_ = value
  
  @property
  def extension(self):
    s = self.name.split(".")
    if len(s) == 1: return ""
    return s[-1]
  
  @property
  def size(self) -> int:
    return len(self.data)
  
  @property
  def isRoot(self) -> bool:
    # Determines if this file is a root
    return self.parent is None  # or type(self.parent) is Link

  @property
  def path(self) -> str:
    if self.isRoot: return self.name
    return f"{self.parent.path}/{self.name}"
  
  @property
  def root(self) -> Dir:
    # Returns this file if it is a root
    # Returns the root of its parent otherwise.
    if self.isRoot:
      return self
    return self.parent.root
  
  def isDescendantOf(self, dir: Dir) -> bool:
    current = self
    while current is not None:
      if current.parent is dir: return True
      current = current.parent

  @staticmethod
  def generate(size: int, name:str="") -> File:
    alphabet = string.ascii_letters + string.digits
    if name == "":
      name = ''.join(secrets.choice(alphabet) for _ in range(size))
    data:str = ''.join(secrets.choice(alphabet) for _ in range(size))
    return File(name, data)

  def rename(self, new_name: str) -> bool:
    if self.isRoot:
      self.name = new_name
      return True
    return self.parent.renameFile(self.name, new_name)
  
  def edit(self, new_data:str, caller:str='File.edit') -> bool:
    if self.isDir: return False
    self.data = new_data
    return True


class Link(File):
  def __init__(self, name: str, target: File = None, parent: Dir | None = None):
    super().__init__(name, "", parent)
    self.target = target

class Dir(File):

  def __init__(self, name: str, data: Dict[str, File]=None, parent:Dir|None=None):
    # super().__init__(name, "", parent)
    self.name: str = name
    self.parent: Dir | None = parent
    self._data_: Dict[str, File] = {} if data is None else data

  @property
  def isDir(self): return True

  @property
  def data(self) -> Dict[str, File]:
    return self._data_

  @property
  def size(self) -> int:
    return sum(f.size for f in self.data.values())
  
  @property
  def capacity(self) -> int:
    return self._capacity_

  @capacity.setter
  def capacity(self, value: int):
    if value < 0:
      self._capacity_ = -1
    elif self.size <= value:
      self._capacity_ = value
    else:
      print("WARNING: Something attempted to set a file's capacity below its size.")
  
  def getFiles(self) -> list[File] | None:
    return list(self.data.values())
  
  def getFile(self, name: str) -> File | None:
    return self.data.get(name, None)

  def addFile(self, file:File, replace:bool=False, caller:str='Dir.addFile') -> bool:
    if file is self:
      return False
    
    if self.getFile(file.name):
      if not replace:
        print(f"{caller}: cannot add file '{file.name}': already exists")
        return False
      else:
        print(f"f{caller}: Warning: Replacing file '{file.name}'")
    
    rootCap = self.root.capacity
    if rootCap > 0 and self.root.size + file.size > rootCap:
      print(f"{caller}: cannot add file '{file.name}': not enough space")
      return False
    
    self.data[file.name] = file
    file.parent = self
    return True
  
  def readFile(self, name:str) -> str | None:
    tgt = self.getFile(name)
    if tgt is None: return None
    if tgt.isDir: return None
    return tgt.data

  def editFile(self, name:str, new_data:str) -> bool:
    tgt = self.getFile(name)
    if tgt is None: return False
    if tgt.isDir: return False
    return tgt.edit(new_data)
    
  def removeFile(self, name:str, recursive:bool=False) -> File | None:    
    tgt = self.getFile(name)
    if tgt is None: return None

    if isinstance(tgt, Dir) and not recursive:
      print(f"rm: cannot remove '{tgt.name}': is directory with contents")
      return None

    tgt.parent = None
    self.data.pop(tgt.name)
    return tgt
  
  def renameFile(self, old_name:str, new_name: str) -> bool:
    tgt = self.getFile(old_name)
    if tgt is None: return False

    if self.getFile(new_name) is not None: return False
    tgt.name = new_name
    self.data[new_name] = self.data.pop(old_name)
    return True
  

class FileSystem:
  
  def __init__(self, capacity, root: Dir | None = None):
    self.root = Dir('') if root is None else root
    self.capacity = capacity

  @property
  def name(self):
    return self.root.name
  
  def resolve(self, pathlist: list[str], fromDir: Dir) -> File | None: ...

  def mkdir(self, targetPathList: list[str]): ...
  def mkfile(self, targetPathList: list[str], filename: str, data: str = ''): ...
