import secrets, string, hashlib, json
from typing import Dict
from .const import *
from .colors import color
from copy import deepcopy
from pathlib import Path
from .util import clamp

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
  def root(self) -> Dir | None:
    """
    The root File or Dir of this File.

    If this file does not have a parent, then
    this property is equivalent to this File itself.
    """
    if self._parent_ is None: return None
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

  def rename(self, new_name: str, test_dir:Dir|None=None) -> bool:
    """
    Renames this file with the new name.
    - If the file has no parent, it simply renames itself. Otherwise,
    it renames itself by calling the `Dir.renameFile()` method of its parent.
    - If `test_dir` is specified, checks if renaming the file as if it is within the dir is successful.
    - If the rename is successful, returns `True`.
    """
    # test_dir specified; check if it can be renamed there
    if test_dir is not None:
      return test_dir.getFile(new_name) is not None

    # orphan; rename self
    if self._parent_ is None:
      self._name_ = new_name
      return True
    
    # not orphan; have parent rename the file
    return self._parent_.renameFile(self._name_, new_name)
  
  def edit(self, new_data) -> bool:
    """
    Replaces this file's data with `new_data`. Returns `True` if successful.
    """
    if self.isDir: return False
    self._data_ = str(new_data)
    return True
  
  def remove(self, markDeleted: bool = True, test:bool = False) -> File | None:
    """
    Removes itself from its own parent.
    - If `markDeleted` is `False`, does not mark itself as deleted.

    Returns itself if successful; returns None otherwise.
    """
    if self._parent_ is None: return self  # file orphaned; considered removed
    if self._parent_.removeFile(self._name_, True, markDeleted=markDeleted, test=test):
      return self
    else:
      return None
    
  def to_json(self, parent:int=-1) -> dict:
    """
    Returns a dictionary object representative of this file:
    ```
    {
      "name": self.name,
      "data": self.data,
      "parent": -1,
      "type": "dir" | "file" | "link"
    }
    ```
    """
    fileType = "file"
    if isinstance(self, Dir): fileType = "dir"
    elif isinstance(self, Link): fileType = "link"
    return {
      "name": self.name,
      "data": self.data,
      "parent": parent,
      "type": fileType
    }

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
  def target(self) -> File | None:
    """
    Returns the targeted file.
    """
    if self._target_ is None: return None
    if self._target_.deleted or self._target_.path != self._data_:
      self._target_ = None
    return self._target_

  def edit(self, new_data: File) -> bool:
    """
    Changes this link's target. The file must be a within this link's root.
    """
    if self.root is None: return False
    if not new_data.isDescendantOf(self.root): return False
    self._target_ = new_data
    self._data_ = new_data.path
    return True

  def open(self) -> File | None:
    """
    Returns the `File` this link links to. Returns `None` if the file is nonexistent within the root this link is in.
    """

    # Get this link's root  If the root is not a dir, we cannot navigate the path.
    if not isinstance(self.root, Dir):
      return None
    
    # The path is guaranteed to be a properly formatted absolute path.
    # No ".", no "..". 
    current: File | Dir = self.root
    pathList = self._data_.split("/")[1:]
    
    # Simple file path traversal.
    for i in range(len(pathList)):
      if isinstance(current, Dir): next = current.getFile(pathList[i])
      elif isinstance(current, File) and i < len(pathList) - 1: return None
      else: return None
      if next is None: return None
      current = next
    
    return current
    

class Dir(File):

  def __init__(self, name: str, data: Dict[str, File] | None =None, parent:Dir|None=None):
    # super().__init__(name, "", parent)
    if len(name) <= 0:
      raise Exception("Cannot make empty named dir")
    self._name_: str = name
    self._parent_: Dir | None = parent
    self._data_: Dict[str, File] = {} if data is None else data

  @property
  def root(self) -> Dir:
    if self._parent_ is None: return self
    return self._parent_.root

  @property
  def isDir(self):
    """
    Returns `True`.
    """
    return True
  
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
  def data(self) -> str:
    return str(self)
  
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
  def files(self) -> tuple[File, ...]:
    """
    Returns a tuple of all the `File` objects it "contains" i.e. points to.
    """
    return tuple(self._data_.values())

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

  def addFile(self, file:File, replace:bool=False, merge:bool=True, deep_merge: bool = False, test:bool=False, test_name:str='') -> bool:
    """
    Adds a file to this directory. If a `Dir` of the same name already exists, and the argued file is a `Dir` itself,
    the two are merged. Unless `deep_merge` is set to `True`, merging will fail if the existing file and the file to be
    added have at least one `Dir` name in common.
    
    - If `replace` is `True`, the argued file replaces any existing file with the same name, whether either are `Dir`s or not.
    - If `merge` is `False`, then this function fails upon attempting to merge the argued `Dir` with the existing `Dir`
    - If `test` is `True`, then this function returns whether it can add the file or not.
    
    Returns `True` if successful.
    """
    if file is self:
      return False
    
    existingFile: File | None
    if not test or test_name == '':
      existingFile = self.getFile(file.name)
    else:
      existingFile = self.getFile(test_name)

    # Cases: attempt to add a file with existing file name.
    if existingFile is not None:
      if not replace and isinstance(existingFile, Dir) and isinstance(file, Dir) and merge:
        # CASE: Existing and new file are both Dirs

        # Check mergability.
        # In doing this, merge is false by default to prevent potentially
        # large recursion stacks. If merge is false, then if the existing file and
        # the file to be added have a folder in common, then the merge fails,
        # and the file won't be added.
        canMerge = True
        for child in file.files:
          canMerge = existingFile.addFile(child, replace=False, merge=deep_merge, test=True)
          if not canMerge: break

        if canMerge:
          if not test:
            for child in file.files:
              existingFile.addFile(child, replace=False, merge=False)      
            file._parent_ = self
            file.markDeleted(False)
          return True
        else:
          return False
      
      elif not replace:
        # CASE: Either file is a Dir or not
        return False
    
    if not test:
      self._data_[file.name] = file
      file._parent_ = self
      file.markDeleted(False)
    return True
      
  def removeFile(self, name:str, recursive:bool=False, markDeleted: bool = True, test:bool=False) -> File | None:    
    """
    Removes the `File` with the specified name.
    - If `recursive` is True, this method can remove non-empty folders.
    - If `markDeleted` is True, this method marks itself (and its children, if this is a `Dir`) as deleted.
    - If `test` is `True`, this is functionally equivalent to `getFile()`.
    Returns the removed file if successful.
    """
    tgt = self.getFile(name)
    if tgt is None: return None

    if isinstance(tgt, Dir):
      if not recursive:
        print(f"rm: cannot remove '{tgt.name}': is directory with contents")
        return None

    if not test:
      tgt._parent_ = None
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
    tgt._name_ = new_name
    self._data_[new_name] = self._data_.pop(old_name)
    return True
  

class FileSystem:
  """
  Class responsible for handling paths, file edits.
  """
  
  def __init__(self, capacity: int, root: Dir | None = None):
    self.root = Dir('~') if root is None else root
    self._capacity_: int = capacity
    self._free_: int = capacity

  @property
  def name(self):
    return self.root.name
  
  @property
  def capacity(self) -> int:
    return self._capacity_

  @property
  def free(self) -> int:
    return self._free_
  
  @free.setter
  def free(self, x: int):
    self._free_ = clamp(x, 0, self.capacity)

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

  def resolve(self, from_dir: Dir, path: str | list[str]) -> File | None:
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
    else:
      # should not be reached
      return None
    
    current = from_dir
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

      next = current.getFile(pathlist[i])

      if type(next) is Link:
        if next.target is None:
          return None
        next = next.target

      current = next
    
    return current

  def mkfile(self, from_dir: Dir, path: str, data: str = '', isDir:bool=False) -> bool:
    """
    Creates a file at the specified path. Returns `True` if successful.
    """
    # get parent
    pathlist = self.parsePath(path)
    parent = self.resolve(from_dir, pathlist[:-1])
    if parent is None: return False
    if not isinstance(parent, Dir): return False
    
    # make new file
    new: File | Dir 
    if isDir: new = Dir(pathlist[-1])
    else: new = File(pathlist[-1], data)

    if new.size > self.free:
      return False
    
    # add file
    addSuccess = parent.addFile(new)

    if addSuccess:
      self.free -= new.size
      
    return addSuccess
  
  def mkdir(self, fromDir: Dir, path: str) -> bool:
    """
    Creates a directory at the specified path. The last name in the string path is the name of the newly created directory.
    
    Returns `True` if successful.
    """
    return self.mkfile(fromDir, path, isDir=True)

  def addFile(self, from_dir: Dir, path: str, file: File, replace:bool=False, merge:bool=True, deep_merge:bool=False, copy:bool=True) -> bool:
    """
    Adds a file into the FileSystem at the specified `path`.
    If the path is nonexistent, the file is added as the specified path.

    This is intended to be used when tranferring files between different filesystems.
    The file must be obtained from the source filesystem via `FileSystem.rm()`, then
    added to the destination filesystem via `FileSystem.addFile()`.

    For more info on `replace`, `merge` and `deep_merge`, see `FileSystem.cp()`.
    
    Returns `True` if successful.
    """

    if file.size > self.free: return False
    
    # if file is not to be copied but can't be removed, return False
    if copy: file = deepcopy(file)
    elif file.remove(test=True) is None: return False

    # get destination dir
    dst_pathlist = self.parsePath(path)
    dst_dir = self.resolve(from_dir, dst_pathlist)
    
    addSuccess: bool = False

    if dst_dir is None:
      # destination dir does not exist
      # get second last file, must be dir
      dst_name = dst_pathlist[-1]
      dst_pathlist = dst_pathlist[:-1]
      dst_dir = self.resolve(from_dir, dst_pathlist)
      if not isinstance(dst_dir, Dir): return False
      
      if not copy: file.remove()

      # rename file
      file.rename(dst_name)
      
      # add file
      addSuccess = dst_dir.addFile(file, replace=replace, merge=merge, deep_merge=deep_merge)
    
    elif isinstance(dst_dir, Dir):
      # destination dir exists, put file there
      if not copy: file.remove()
      addSuccess = dst_dir.addFile(file, replace=replace, merge=merge, deep_merge=deep_merge)
      
    elif replace:
      # destination dir is actually non-dir, replace
      dst_dir = dst_dir.parent
      if not isinstance(dst_dir, Dir): return False
      addSuccess = dst_dir.addFile(file, replace=replace, merge=merge, deep_merge=deep_merge)

    if addSuccess:
        self.free -= file.size
    return addSuccess
  
  def rm(self, fromDir: Dir, path: str, recursive: bool = False) -> File | None:
    """
    Removes the file or directory within the FileSystem at the specified path.

    Returns the removed file or directory if successful.
    """
    # Retrieve the File to be removed
    pathlist = self.parsePath(path)
    tgt = self.resolve(fromDir, pathlist)
    if tgt is None: return None
    if isinstance(tgt, Dir) and (len(tgt.files) > 0 and not recursive): return None
    
    # Get its parent
    parent = tgt.parent
    if parent is None: return None

    rmSuccess = parent.removeFile(tgt.name, recursive)
    if rmSuccess is not None: self.size += rmSuccess.size
    return rmSuccess
  
  def rmdir(self, fromDir: Dir, path: str, recursive: bool=False) -> File | None:
    """
    Removes the directory. Returns the removed directory if successful.
    """
    return self.rm(fromDir, path, recursive=recursive)
  
  def cp(self, from_dir: Dir, from_path: str, to_path: str, replace:bool=False, merge:bool=True, deep_merge:bool=False, mv:bool=False) -> bool:
    """
    Copies a file specified via `from_path` into `to_path`.
    - If `to_path` doesn't exist, the copied file is renamed into the last name in `to_path`.
    - If `mv` is `True`, this removes the file to be copied after the operation is complete.
    - If `replace` is `True` and `to_path` refers to a non-directory, that non-directory is replaced.
    - If `merge` is `True` and both `from_path` and `to_path` refers to directories, the directories are merged.
      - Directory merging can fail if both have immediate descendants (children) that match names.
      - If `deep_merge` is `True`, and the children with matching names are directories, then those child directories are merged.
        The merge can still fail if they end up having a common descendant path.

    For more information o 

    Returns `True` if the copy is successful.
    """

    # retrieve file to copy
    from_file: File | None = self.resolve(from_dir, self.parsePath(from_path))
    if from_file is None: return False
    if not mv: from_file = deepcopy(from_file)

    # if copy, check if FileSystem can still accomodate copy of retrieved file
    if not mv and from_file.size > self.free: return False
    
    # retrieve destination to copy file to
    dst_path = self.parsePath(to_path)
    to_file = self.resolve(from_dir, dst_path)

    # CASES
    # FIXME: refactor me
    if to_file is None:
      # destination dir does not exist, rename the file

      # get the second last dir in the target path
      dst_name = dst_path[-1]
      dst_path = dst_path[:-1]
      to_file = self.resolve(from_dir, dst_path)
      if to_file is None: return False
      if not isinstance(to_file, Dir): return False
      
      # TESTS
      # (mv) test if the file can be removed
      if mv and from_file.remove(markDeleted=False, test=True) is None: return False
      # (cp) rename the file; this is safe since the file is a deep copy
      if not mv: from_file.rename(dst_name)
      # test if the (renamed) file can be added to the target directory
      if not to_file.addFile(from_file, replace=replace, merge=merge, deep_merge=deep_merge, test=True, test_name=dst_name): return False
      
      # execute
      if mv:
        from_file.remove(markDeleted=False)
        from_file.rename(dst_name)
      to_file.addFile(from_file, replace=replace, merge=merge, deep_merge=deep_merge)
      self.free -= from_file.size
      return True
    
    elif isinstance(to_file, Dir):
      # destination dir exists, put from_file in there
      
      # TESTS
      # (mv) test if the file can be removed
      if mv and from_file.remove(markDeleted=False, test=True) is None: return False
      # test if the copied file can be added to the target directory
      if not to_file.addFile(from_file, replace=replace, merge=merge, deep_merge=deep_merge, test=True): return False
      
      # execute
      if mv: from_file.remove(markDeleted=False)
      to_file.addFile(from_file, replace=replace, merge=merge, deep_merge=deep_merge)
      self.free -= from_file.size
      return True
    elif replace:
      # destination dir is actually non-dir, replace
      to_file = to_file.parent
      if not isinstance(to_file, Dir): return False
      
      # TESTS
      # (mv) test if the file can be removed
      if mv and from_file.remove(markDeleted=False, test=True) is None: return False
      # test if the copied file can be added to the target directory
      if not to_file.addFile(from_file, replace=replace, merge=merge, deep_merge=deep_merge, test=True): return False

      # execute
      if mv: from_file.remove(markDeleted=False)
      to_file.addFile(from_file, replace=replace, merge=merge, deep_merge=deep_merge)
      self.free -= from_file.size

      return True
    
    else:
      # destination dir is non-dir but replace is false, fail
      return False

  def mv(self, from_dir: Dir, from_path: str, to_path: str, replace:bool=False, merge:bool=True, deep_merge:bool=False) -> bool:
    """
    Moves the file specified by `from_path` into `to_path`. If `to_path` is nonexistent, the file is renamed into `to_path`.

    This is basically a `FileSystem.cp()` call with `mv=True`. For more information, see `FileSystem.cp()`.
    
    Returns `True` if successful.
    """
    return self.cp(from_dir, from_path, to_path, replace=replace, merge=merge, deep_merge=deep_merge, mv=True)
  
  def rename(self, from_dir: Dir, from_path: str, to_name: str) -> bool:
    """
    Renames the file specified by `from_path` into `to_name`. Returns `True` if successful.
    """
    tgt_file: File | None = self.resolve(from_dir, self.parsePath(from_path))
    if tgt_file is None: return False
    return tgt_file.rename(to_name)

