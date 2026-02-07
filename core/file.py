import secrets, string, hashlib, json
from typing import Dict
from .const import *
from .colors import color
from copy import deepcopy
from pathlib import Path

# For simplicity, the data size unit isn't bytes (because Unicode is a thing), it's "Chomp".

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
  - `deleted`
  
  **Methods:**
  - `isDescendantOf`
  - `markDeleted`
  - `rename`
  - `remove`
  - `edit`

  **Static Methods**
  - `generate`
  """

  def __init__(self, name:str, data="", parent:Dir|None=None):
    if len(name) <= 0:
      raise Exception("Error creating File: len(name) is zero")
    self._name_: str = name
    self._parent_: Dir | None = parent
    self._data_ = data
    self.deleted = False

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
  
  def __str__(self) -> str:
    return self.path + ":" + self._data_
  
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

    Since unicode is a thing, the file size unit of measurement in this game
    is called a "Chomp" (ch)
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
  
  def markDeleted(self, deleted: bool=True):
    """
    Makes the file marks itself as deleted, i.e. sets its `deleted` property to True or the value specified by `deleted`.
    """
    self.deleted = deleted and True
  
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
  
  def remove(self, markDeleted: bool = True) -> File:
    """
    Removes itself from its own parent.
    - If `markDeleted` is `False`, does not mark itself as deleted.

    Returns itself if successful; returns None otherwise.
    """
    if self._parent_.removeFile(self._name_, True, markDeleted):
      return self
    else:
      return None

class Link(File):
  """
  Subclass of `File`.
  
  Unlike `File`:
  - This `File` requires a `parent`.
  - The `data` property of this file is the path to a file within its root.
  - The `path` property returns this `File`'s `data`.
  - This `File` is always 1 ch large.
  """
  def __init__(self, name: str, target: File, parent: Dir):
    if not target.isDescendantOf(parent.root): return False
    super().__init__(name, target.path, parent)
    self._target_ = target

  @property
  def size(self) -> int:
    """
    The size of this link. Always exactly 1 ch.
    """
    return 1
  
  @property
  def path(self) -> str:
    """
    Returns the path to this link's target `File`.
    """
    return self._data_
  
  @property
  def target(self) -> File:
    """
    Returns the targeted file.
    """
    if self._target_.deleted or self._target_.path != self._data_:
      self._target_ = None
    return self._target_

  def edit(self, new_target: File) -> bool:
    """
    Changes this link's target. The file must be a within this link's root.
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
    if len(name) <= 0:
      raise Exception("Cannot make empty named dir")
    self._name_: str = name
    self._parent_: Dir | None = parent
    self._data_: Dict[str, File] = {} if data is None else data

  @property
  def isDir(self):
    """
    Returns `True`.
    """
    return True

  @property
  def data(self) -> tuple[File]:
    """
    Returns a tuple of the `File`s it contains.

    To get a formatted version for `ls`, try stringifying this `Dir` i.e. via `str()`
    """
    return tuple(self._data_.values())
  
  def __str__(self) -> str:
    ls = []
    for filename, file in self._data_.items():
      if isinstance(file, Dir):
        ls += [color(filename, bcolors.DIR)]
      elif isinstance(file, Link):
        ls += [color(filename, bcolors.LINK)]
      else:
        ls += [filename]
    return "\n".join(ls)
  
  @property
  def ls(self) -> tuple[tuple[str, int]]:
    """
    Returns a tuple of filenames and integers, with the integers corresponding to the following type:
    |Type|Thing|
    |-|-|
    |`File`|0|
    |`Link`|1|
    |`Dir`|2|
    """
    ls = []
    for filename, file in self._data_.items():
      if isinstance(file, Dir):
        ls += (filename, 2)
      elif isinstance(file, Link):
        ls += (filename, 1)
      else:
        ls += (filename, 0)
    return tuple(ls)

  @property
  def size(self) -> int:
    """
    Returns the sum of the file sizes of the files it contains plus 1 ch.
    """
    return sum(f.size for f in self._data_.values()) + 1
  
  def markDeleted(self, deleted: bool = True):
    self.deleted = deleted and True
    for file in self._data_.values():
      file.markDeleted(deleted)
  
  def getFile(self, name: str) -> File | None:
    """
    Returns the file with the specified name. Returns None if it doesn't exist.
    """
    return self._data_.get(name, None)

  def addFile(self, file:File, replace:bool=False, merge:bool=True, deepMerge: bool = False, test:bool=False, caller:str='Dir.addFile') -> bool:
    """
    Adds a file to this directory. If a `Dir` of the same name already exists, and the argued file is a `Dir` itself,
    the two are merged. Unless `deepMerge` is set to `True`, merging will fail if the existing file and the file to be
    added have at least one `Dir` name in common.
    
    - If `replace` is `True`, the argued file replaces any existing file with the same name, whether either are `Dir`s or not.
    - If `merge` is `False`, then this function fails upon attempting to merge the argued `Dir` with the existing `Dir`
    - If `test` is `True`, then this function returns whether it can add the file or not.
    
    Returns `True` if successful.
    """
    if file is self:
      return False
    
    existingFile: File | None = self.getFile(file.name)

    # Cases: attempt to add a file with existing file name.
    if existingFile is not None:
      if replace:
        print(f"f{caller}: Warning: Replacing file '{file.name}'")
      
      elif isinstance(existingFile, Dir) and isinstance(file, Dir) and merge:
        # CASE: Existing and new file are both Dirs

        # Check mergability.
        # In doing this, merge is false by default to prevent potentially
        # large recursion stacks. If merge is false, then if the existing file and
        # the file to be added have a folder in common, then the merge fails,
        # and the file won't be added.
        canMerge = True
        for child in file.data:
          canMerge = existingFile.addFile(child, replace=False, merge=deepMerge, test=True)
          if not canMerge: break

        if canMerge:
          if not test:
            print(f"{caller}: Merging '{file.name}' into '{self.path}'...")
            for child in file.data:
              canMerge = existingFile.addFile(child, replace=False, merge=False)      
            file.parent = self
            file.markDeleted(False)
          return True
        else:
          print(f"{caller}: Failed: cannot merge dir '{file.name}'")
          return False
      
      elif not replace:
        # CASE: Either file is a Dir or not
        print(f"{caller}: cannot add file '{file.name}': already exists")
        return False
    
    if not test:
      self._data_[file.name] = file
      file.parent = self
      file.markDeleted(False)
    return True
      
  def removeFile(self, name:str, recursive:bool=False, markDeleted: bool = True) -> File | None:    
    """
    Removes the `File` with the specified name.
    - If `recursive` is True, this method can remove non-empty folders.
    - If `markDeleted` is True, this method marks itself (and its children, if this is a `Dir`) as deleted.

    Returns the removed file if successful.
    """
    tgt = self.getFile(name)
    if tgt is None: return None

    if isinstance(tgt, Dir):
      if not recursive:
        print(f"rm: cannot remove '{tgt.name}': is directory with contents")
        return None

    tgt.parent = None
    tgt.markDeleted(markDeleted)
    self._data_.pop(tgt.name)
    return tgt
  
  def renameFile(self, old_name:str, new_name: str) -> bool:
    """
    Renames the file with name `old_name` into `new_name`.
    
    Called by its children if `rename` is called.
    """
    tgt = self.getFile(old_name)
    if tgt is None: return False

    if self.getFile(new_name) is not None: return False
    tgt.name = new_name
    self._data_[new_name] = self._data_.pop(old_name)
    return True
  

class FileSystem:
  """
  Class responsible for handling paths, file edits.
  """
  
  def __init__(self, capacity, root: Dir | None = None):
    self.root = Dir('~') if root is None else root
    self.capacity = capacity

  @property
  def name(self):
    return self.root.name

  # Normalizes path; removes redundant directory names, `.` calls, repetitive slashes
  # normalizes backslashes
  def parsePath(self, pathstr: str, normalize: bool=False) -> list[str]:
    """
    Corrects a path it by:
    - Converting backslashes to slashes
    - Removing "." calls and empty directories
    - removing redundant ".." calls, if `normalize` is `True`

    It then returns the list of filenames to traverse.
    
    `resolve()` should use the return value of this function.

    """
    pathstr = pathstr.replace("\\", "/")
    pathlist = [x for x in pathstr.split("/") if x not in (".", "")]
    if normalize:
      pathstack = []
      for file in pathlist:
        if file == "..":
          if len(pathstack) <= 0 or pathstack[-1] == "..":
            pathstack += [file]
          else:
            pathstack.pop()
          continue
        pathstack += [file]
      pathlist = pathstack

    return pathlist

  def resolve(self, path: str | list[str], fromDir: Dir) -> File | None:
    """
    Returns the file specified by the path. Returns `None` if the file doesn't exist,
    or if the path attempts to traverse inside a `File`.

    `Link`s are treated as the files they point to.
    """
    pathlist: list[str]
    if type(path) is list:
      pathlist = path
    elif type(path) is str:
      pathlist = self.parsePath(path)
    
    current = fromDir
    if pathlist[0] == self.root.name:
      pathlist = pathlist[1:]
      current = self.root
    
    pathlen = len(pathlist)
    for i in range(pathlen):

      if current is None:
        return None
      
      # path terminates on file prematurely
      if not isinstance(current, Dir):
        if i < pathlen - 1:
          return None
        else:
          return current

      next = current.getFile(pathlen[i])

      if type(next) is Link:
        if next.target is None:
          return None
        next = next.target

      current = next
    
    return current
  

  def mkdir(self, path: str, fromDir: Dir) -> bool:
    """
    Creates a directory at the specified path. Returns `True` if successful.
    """
    pathlist = self.parsePath(path)
    parent: Dir | None = self.resolve(pathlist[:-1], fromDir)
    if parent is None: return False
    new = Dir(pathlist[-1])
    return parent.addFile(new)
    

  def mkfile(self, path: str, fromDir: Dir, data: str = '') -> bool:
    """
    Creates a file at the specified path. Returns `True` if successful.
    """
    pathlist = self.parsePath(path)
    parent: Dir | None = self.resolve(pathlist[:-1], fromDir)
    if parent is None: return False
    new = File(pathlist[-1], data)
    return parent.addFile(new)
  
  def rmdir(self, path: str, fromDir: Dir, recursive: bool=False) -> File | None:
    "Removes the directory. Returns the removed directory if successful."
    pathlist = self.parsePath(path)
    tgt: Dir | None = self.resolve(pathlist, fromDir)
    if tgt is None: return None
    if not isinstance(tgt, Dir): return None
    parent = tgt.parent
    if parent is None: return None
    return parent.removeFile(tgt.name, recursive)

  def mv(self, from_path: str, to_path: str, replace: bool = False) -> bool:
    tgt_file: File = self.resolve(self.parsePath(from_path))
    if tgt_file is None: return False
    dst_path = self.parsePath(to_path)
    dst_dir: Dir = self.resolve(dst_path)
    if dst_dir is None:
      # Case 1: nonexistent; recreate from_path as to_path
      dst_name = dst_path[-1]
      dst_dir = self.resolve(dst_path[:-1])
      if dst_dir.addFile(tgt_file.remove(False), replace=replace):
        return tgt_file.rename(dst_name)
      else:
        return False
    else:
      # Case 2: path exists; put it inside
      return dst_dir.addFile(tgt_file.remove(False), replace=replace)
  
  def rename(self, from_path: str, to_name: str) -> bool:
    ...
  
  def cp(self, from_path: str, to_path: str) -> bool:
    ...

