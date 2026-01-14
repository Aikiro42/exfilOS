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
  def __init__(self, name:str, data:str="", parent:Dir|None=None):
    self.name: str = name
    self.parent: Dir | None = parent
    self.data: str = data
  
  @property
  def extension(self):
    s = self.name.split(".")
    if len(s) == 1: return ""
    return s[-1]
  
  @property
  def size(self):
    return len(self.data)
  
  @property
  def path(self):
    if self.parent is None: return self.name
    return f"{self.parent.path}/{self.name}"
  
  @property
  def root(self):
    if self.parent is None: return self
    return self.parent.root

  @staticmethod
  def generate(size: int, name:str="") -> File:
    alphabet = string.ascii_letters + string.digits
    if name == "":
      name = ''.join(secrets.choice(alphabet) for _ in range(size))
    data:str = ''.join(secrets.choice(alphabet) for _ in range(size))
    return File(name, data)

  def rename(self, new_name: str) -> bool:
    return self.parent.renameFile(self.name, new_name)
  
  def edit(self, new_data:str, caller:str='File.edit') -> bool:
    if self.isDir: return False
    if self.root.size - self.size + len(new_data) > self.root.capacity:
      print(f"{caller}: cannot edit file '{self.name}': edit exceeds root capacity")
      return False
    self.data = new_data
    return True

class Dir(File):

  def __init__(self, name: str, data: Dict[str, File]=None, parent:Dir|None=None, capacity:int=-1):
    super().__init__(name, "", parent)
    self.data: Dict[str, File]
    if data is None:
      self.data = {}
    else:
      self.data = data
    self._capacity_ = capacity

  @property
  def size(self) -> int:
    return sum(f.size for f in self.data.values())
  
  @property
  def capacity(self) -> int:
    return self._capacity_

  @capacity.setter
  def capacity(self, value: int):
    if value < 0 or not self.isDir:
      self._capacity_ = -1
    elif self.size <= value:
      self.capacity = value
    else:
      print("WARNING: Something attempted to set a file's capacity below its size.")
  
  def addFile(self, file:File, replace:bool=False, caller:str='Dir.addFile') -> bool:
    # Adds a file into the data of the file
    # this function is called from.
    # Returns true on success, false on failure.
    
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
  
  def getFiles(self) -> list[File] | None:
    return list(self.data.values())
  
  def getFile(self, name: str, pop:bool = False) -> File | None:
    if self.data.get(name, None) is None:
      return None
    if pop:
      return self.data.pop(name)
    else:
      return self.data[name]
  
  def readFile(self, name:str) -> str | None:
    # Returns the contents of the specified file.
    # If the file on which this function is called
    # is not a directory, this function returns
    # the file's contents instead.
    tgt = self.getFile(name)
    if tgt is None: return None
    if isinstance(tgt, Dir): return None
    return tgt.data

  def editFile(self, name:str, new_data:str) -> bool:
    tgt = self.getFile(name)
    if tgt is None: return False
    return tgt.edit(new_data)
    
  def removeFile(self, name:str, recursive:bool=False) -> File | None:
    
    # Attempt to retrieve the file to delete
    tgt = self.getFile(name)
    if tgt is None: return None

    # Validate file; Refuse to delete if key-name mismatch
    if tgt.name != name:
      print("PANIC: file key-name mismatch")
      return None

    # Check if file is a directory
    # Otherwise, report failure to delete
    if isinstance(tgt, Dir) and not recursive:
      print(f"rm: cannot remove '{tgt.name}': is directory with contents")
      return None
    
    # Finally, remove the target
    tgt.parent = None
    self.data.pop(tgt.name)
    return tgt
  
  def renameFile(self, old_name:str, new_name: str) -> bool:
    tgt = self.getFile(old_name, None)
    if tgt is None: return False
    if self.getFile(new_name, None) is not None: return False
    tgt.name = new_name
    self.data[new_name] = self.data.pop(old_name)
    return True

  def toJson(self, jsonPath: str="filesys.json") -> list:
    # dfs algorithm
    self.validateFiles()
    fileQueue = [(self, -1)]
    files = []
    while len(fileQueue) > 0:
      f = fileQueue.pop(0)
      isDir = isinstance(f[0], Dir)
      files.append({
        # "index": len(files),
        "name": f[0].name,
        "capacity": f[0].capacity,
        "parent": f[1],
        "data": None if isDir else f[0].data
      })
      if isDir:
        for child in f[0].data.values():
          fileQueue.append((child, len(files) - 1))
    
    p = Path(jsonPath)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.touch(exist_ok=True)
    p.write_text(json.dumps(files, indent=2))

    # with open(jsonPath, "w") as jsonFile:
    #   jsonFile.write(json.dumps(files))
    return files

  @staticmethod
  def fromJson(jsonPath: str) -> File:
      files: list[File] = []
      p = Path(jsonPath)
      with p.open() as jsonObj:
        fileDefs: list[dict] = json.loads(jsonObj.read())
        for fileDef in fileDefs:
          isDir = fileDef.get("data", None) is None
          newFile: File
          if isDir:
            newFile = Dir(fileDef["name"], data={}, capacity=fileDef["capacity"])
          else:
            newFile = File(fileDef["name"], data=fileDef["data"])
          files.append(newFile)
          parentIndex: int = fileDef["parent"]
          if fileDef["parent"] > -1:
            d = files[parentIndex]
            if isinstance(d, Dir):
              d.addFile(newFile)
      return files[0]
  
class Cache(Dir):
  
  def __init__(self, name:str="cache", capacity:int=2**8):  
    super().__init__(name, capacity=capacity)
  
  def toJson(self, jsonPath: str = "cache.json") -> list:
    return super().toJson(jsonPath)
  
  @classmethod
  def fromDir(cls, dir: Dir) -> Cache:
    c = cls(name=dir.name, capacity=dir.capacity)
    c.data = dir.data
    return c
  
class FileSystem:
  def __init__(self, name:str="~", root:Dir|None=None, capacity:int=-1):
    self.root: Dir
    if root is None:
      self.root = Dir(name, capacity=capacity)
    else:
      self.root = root
    
  @property
  def name(self):
    return self.root.name

  @property
  def size(self):
    return self.root.size
  
  @property
  def capacity(self):
    return self.root.capacity

  def listFiles(self, f: Dir) -> list[File] | None:
    return f.getFiles()

  def mkfile(self, f: Dir, name: str, replace: bool=False) -> File | None:
    newFile = File(name)
    if f.addFile(newFile, replace=replace, caller='FileSystem.mkfile'):
      return newFile
    else:
      return None
  
  def mkdir(self, f: Dir, name: str, capacity: int = -1) -> Dir:
    newFile = Dir(name, capacity=capacity)
    if f.addFile(newFile, caller='FileSystem.mkfile'):
      return newFile
    else:
      return None
  
  def rm(self, f: File, recursive:bool=False, caller:str='FileSystem.rm') -> File | None:
    return f.parent.removeFile(f.name, recursive=recursive)
    
  def mv(self, tgt: File, dst: Dir) -> bool:
    if tgt.parent is None: return False
    if tgt.parent.removeFile(tgt.name, recursive=True) is not None:
      return dst.addFile(tgt, caller='FileSystem.mv')
      
  def cp(self, tgt: File, dst: Dir) -> bool:
    return dst.addFile(tgt, caller='FileSystem.cp')

  def rename(self, tgt: File, name: str) -> bool:
    return tgt.rename(name)
  