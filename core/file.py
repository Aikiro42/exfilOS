import secrets, string, hashlib, json
from typing import Dict
from .const import *
from .colors import color
from copy import deepcopy
from pathlib import Path

RESERVED_NAMES = [
  ROOT_NAME,
  "cache",
]

class File:
  """
  Superclass for `File`s, `Dir`ectories and `Link`s. The building block of this game's filesystem.

  **Properties:**
  - `name`
  - `data`
  - `parent`
  - `isDir`
  - `extension`
  - `size`
  - `path`
  - `root`
  **Methods:**
  - `isDescendantOf`
  - `generate`
  - `rename`
  - `edit`
  """

  def __init__(self, name:str, data="", parent:Dir|None=None):
    if len(name) <= 0:
      raise Exception("Error creating File: len(name) is zero")
    self._name_: str = name
    self._parent_: Dir | None = parent
    self._data_ = data

  @property
  def name(self) -> str:
    """
    The name of this file.
    """
    return self._name_
  
  @property
  def parent(self) -> Dir | None:
    """
    The `Dir` parent of this `File`. Can be `None` if this is a root.
    """
    return self._parent_

  @property
  def isDir(self) -> bool:
    """
    Returns if this `File` is a Dir or not.
    """
    return False

  @property
  def data(self) -> str:
    """
    The raw data of this `File` as a string.
    """
    return self._data_
  
  @property
  def extension(self) -> str:
    """
    The extension of this file.
    - If this File's name is `"hello.txt"`, then the extension is `"txt"`
    - If this File's name is `"hello.txt.mp4"`, then the extension is `"mp4"`
    - If this File's name is `"hello."`, then the extension is `""`
    - If this File's name is `"hello.."`, then the extension is `""`
    - If this File's name is `"hello"`, then the extension is `""`
    """
    s = self._name_.split(".")
    if len(s) == 1: return ""
    return s[-1]
  
  @property
  def size(self) -> int:
    """
    This file's size, i.e. the length of the raw data string.
    """
    return len(self._data_)
  
  # A file can never be a root.
  # This snippet is retained and commented for posterity.
  # @property
  # def isRoot(self) -> bool: return self._parent_ is None  # or type(self._parent_) is Link

  @property
  def path(self) -> str:
    """
    The absolute path of this File.
    
    If this File does not have a parent, then this is
    equivalent to this File's `name`.
    """
    if self._parent_ is None: return self._name_
    return f"{self._parent_.path}/{self._name_}"
  
  @property
  def root(self) -> File:
    """
    The root File or Dir of this File.

    If this file does not have a parent, then
    this property is equivalent to this File itself.
    """
    if self._parent_ is None: return self
    return self._parent_.root
  
  def isDescendantOf(self, dir: Dir) -> bool:
    """
    Determines if this file is inside the specified Dir. Returns `True` if it is, `False` otherwise.
    """
    current = self
    while current is not None:
      if current.parent is dir: return True
      current = current.parent
    return False

  @staticmethod
  def generate(size: int, name:str="") -> File:
    """
    Generates a `size` large File with random data.
    """
    alphabet = string.ascii_letters + string.digits
    if name == "":
      name = ''.join(secrets.choice(alphabet) for _ in range(size))
    data:str = ''.join(secrets.choice(alphabet) for _ in range(size))
    return File(name, data)

  def rename(self, new_name: str) -> bool:
    """
    Renames this file with the new name.
    
    If the file has no parent, it simply renames itself. Otherwise,
    it renames itself by calling the `Dir.renameFile()` method of its parent.
    
    If the rename is successful, returns `True`.
    """
    if self._parent_ is None:
      self._name_ = new_name
      return True
    return self._parent_.renameFile(self._name_, new_name)
  
  def edit(self, new_data:str, caller:str='File.edit') -> bool:
    """
    Replaces this file's data with `new_data`. Returns `True` if successful.
    """
    if self.isDir: return False
    self._data_ = new_data
    return True

class Link(File):
  """
  Subclass of `File`. The `data` property of this file is the path to a file within its root.
  """
  def __init__(self, name: str, target: File, parent: Dir | None = None):
    super().__init__(name, target.path, parent)

  def edit(self, new_target: File) -> bool:
    """
    Changes this link's target.
    """
    if not new_target.isDescendantOf(self.root): return False
    self._target_ = new_target
    self._data_ = new_target.path
    return True

  def open(self) -> File | None:
    """
    Returns the `File` this link links to. Returns `None` if the file is nonexistent within the root this link is in.
    """

    # Get this link's root  If the root is not a dir, we cannot navigate the path.
    if not isinstance(self.root, Dir):
      return None
    current: Dir = self.root
    
    # The path is guaranteed to be a properly formatted absolute path.
    # No ".", no "..". 
    pathList = self._data_.split("/")[1:]
    
    # Simple file path traversal.
    for i in range(len(pathList)):
      next = current.getFile(pathList[i])
      if next is None: return None
      if isinstance(next, File) and i < len(pathList) - 1: return None
      current = next
    
    return current
    

  
    
class Dir(File):

  def __init__(self, name: str, data: Dict[str, File]=None, parent:Dir|None=None):
    # super().__init__(name, "", parent)
    self._name_: str = name
    self._parent_: Dir | None = parent
    self._data_: Dict[str, File] = {} if data is None else data

  @property
  def isDir(self): return True

  @property
  def data(self) -> Dict[str, File]:
    return self._data_

  @property
  def size(self) -> int:
    return sum(f.size for f in self._data_.values())
  
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
    return list(self._data_.values())
  
  def getFile(self, name: str) -> File | None:
    return self._data_.get(name, None)

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
    
    self._data_[file.name] = file
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
    self._data_.pop(tgt.name)
    return tgt
  
  def renameFile(self, old_name:str, new_name: str) -> bool:
    tgt = self.getFile(old_name)
    if tgt is None: return False

    if self.getFile(new_name) is not None: return False
    tgt.name = new_name
    self._data_[new_name] = self._data_.pop(old_name)
    return True
  

class FileSystem:
  
  def __init__(self, capacity, root: Dir | None = None):
    self.root = Dir('') if root is None else root
    self.capacity = capacity

  @property
  def name(self):
    return self.root.name

  # Normalizes path; removes redundant directory names, `.` calls, repetitive slashes
  # normalizes backslashes
  def parsePath(self, pathstr: str) -> list[str]: ...  

  def resolve(self, pathlist: list[str], fromDir: Dir) -> File | None: ...

  def mkdir(self, targetPathList: list[str]): ...
  def mkfile(self, targetPathList: list[str], filename: str, data: str = ''): ...
