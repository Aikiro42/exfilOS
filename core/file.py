import json
from typing import Dict
from .const import *
from .colors import color
from copy import deepcopy

class File:
  def __init__(self, name:str, isDir:bool, data:str|Dict[str, File]="", parent:File|None=None):
    self.isDir: bool = isDir
    self.name: str = name
    self.parent: File | None = parent
    self.data: str | Dict[str, File] = {} if isDir else data

  def __str__(self):
    s = f"{self.name}"
    if self.parent is not None:
      s = f"{self.parent.name}\n└─ {s} <-\n"
    else:
      s += " (ROOT)\n"
    if self.isDir:
      for filename in self.data.keys():
        s += f"{'└─ ' if self.parent is None else '   └─ '}{filename}\n"
    else:
      s += f">> <SOF>{self.data}<EOF>"
    return s
  
  @property
  def path(self):
    if self.parent is None: return self.name
    return f"{self.parent.path}/{self.name}"

  def validateFiles(self, verbose:bool=False) -> bool:
    # Makes sure that all the keys in the directory's data
    # correspond with the name of the file they refer to.
    # Returns True if the files are all valid.
    # Returns False if it validated a file.
    if not self.isDir: return
    didError: bool = False
    for filename, file in self.data.items():
      if file.parent != self:
        if verbose:
          if not didError:
            print(f"WARNING: '{self.path}':")
            didError = True
          print(f"  Detected parent mismatch: {file.parent} != {self}")
        file.parent = self
      if file.name != filename:
        if verbose:
          if not didError:
            print(f"WARNING: '{self.path}':")
            didError = True
          print(f"  Detected hash mismatch: {file.name} != {filename}")
        self.data[file.name] = self.data.pop(filename)
    return not didError
  
  def createFile(self, name:str, isDir:bool) -> File | None:
    # Creates a file within the directory and returns it.
    # Returns the file if it already exists.
    # Returns None if the file on which this function is called
    # is not a directory.
    if not self.isDir: return None
    made = self.getFile(name)
    if made is None:
      made = File(name, isDir, parent=self)
      self.data[name] = made
    return made
  
  def addFile(self, file:File, replace:bool=False, caller:str='') -> bool:
    # Adds a file into the data of the file
    # this function is called from.
    # Returns true on success, false on failure.
    if not self.isDir: return False
    if self.getFile(file.name) and not replace:
      print(f"{'ERROR' if caller == '' else caller}: cannot add file '{file.name}': '{self.path}' already exists")
      return False
    self.data[file.name] = file
    file.parent = self
    return True
  
  def getFile(self, name: str, pop:bool = False) -> File | None:
    # dir operation
    # returns file with filename `name` within itself
    # returns None if file is nonexistent
    if not self.isDir:
      print(f"ERROR: Cannot retrieve file from {self.name}, is file")
      return None
    if name not in self.data.keys():  # FIXME: change to dict.get()?
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
    if not self.isDir: return self.data
    tgt = self.getFile(name)
    if tgt is None: return None
    if tgt.isDir: return None
    return tgt.data

  def editFile(self, name:str, new_data:str) -> bool:
    tgt = self.getFile(name)
    if tgt is None: return False
    if tgt.isDir: return False
    tgt.data = new_data
    return True
    
  def removeFile(self, name:str, recursive:bool=False) -> File | None:
    # Removes a file with the associated name from its File dictionary
    # Returns the removed file if success, None otherwise.
    if not self.isDir: return None
    
    # Attempt to retrieve the file to delete
    tgt = self.getFile(name)
    if tgt is None: return None

    # Validate file; Refuse to delete if key-name mismatch
    if tgt.name != name:
      print("PANIC: file key-name mismatch")
      return None

    # Check if file is a directory
    # Otherwise, report failure to delete
    if tgt.isDir and not recursive:
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
  
  def rename(self, new_name: str) -> bool:
    return self.parent.renameFile(self.name, new_name)
  
    # dir operation
  # lists all files within
  def listFiles(self, all:bool=False, level:int=0):
    if not self.isDir:
      print(f"ERROR: Cannot ls inside {self.name}")
      return
    if all:
      print(f"{'  '*level}{color('.', bcolors.DIR)}")
      print(f"{'  '*level}{color('..', bcolors.DIR)}")
    for filename, file in sorted(self.data.items(), key=lambda x: x[0]): # type: ignore
      if filename[0] == '.' and not all: continue  # skip hidden files
      print(f"{'  '*level}{color(file.name, bcolors.DIR) if file.isDir else file.name}")

  def toJson(self, jsonPath: str="filesys.json") -> list:
    # dfs algorithm
    self.validateFiles()
    fileQueue = [(self, -1)]
    files = []
    while len(fileQueue) > 0:
      f = fileQueue.pop(0)
      files.append({
        # "index": len(files),
        "name": f[0].name,
        "isDir": f[0].isDir,
        "parent": f[1],
        "data": None if f[0].isDir else f[0].data
      })
      if f[0].isDir:
        for child in f[0].data.values():
          fileQueue.append((child, len(files) - 1))
    
    with open(jsonPath, "w") as jsonFile:
      jsonFile.write(json.dumps(files))

    return files

  @staticmethod
  def fromJson(jsonPath: str) -> File:
      files: list[File] = []
      with open(jsonPath) as jsonObj:
        fileDefs = json.loads(jsonObj.read())
        for fileDef in fileDefs:
          isDir = fileDef["isDir"]
          newFile = File(fileDef["name"], isDir, fileDef.get("data", {} if isDir else ""))
          files.append(newFile)
          parentIndex: int = fileDef["parent"]
          if fileDef["parent"] > -1:
            files[parentIndex].addFile(newFile)
      return files[0]



  @staticmethod
  def fromDict(rootDict: dict, rootName: str) -> File:
    rootFile = File(rootName, True)
    for fileName, fileData in rootDict:
      newFile = File(fileName, type(fileData) is not str)
      rootFile.addFile(newFile, caller='fromDict')
    return rootFile



class FileSystem:
  def __init__(self, root:File|None=None):
    self.root = File("~", isDir=True)
    if root is not None:
      if root.isDir:
        self.root=root
    self.cwd = self.root

  @property
  def currentPath(self):
    path = self.cwd.name
    current: File = self.cwd
    while current.parent is not None:
      path = f"{current.parent.name}/{path}"
      current = current.parent
    return path

  def resolvePath(self, pathList: list[str], fromFile:File|None=None, caller:str='') -> File | None:
    # Parameters:
    #   pathList = ordered list of filenames through which to traverse
    # Returns the final file in the path.
    # (remember that dirs are files too)
    # If the path to the file does not exist, returns None.
    path: str = '/'.join(pathList)
    if len(pathList) <= 0: return self.cwd
    current: File | None = self.cwd if fromFile is None else fromFile

    # if first filename in the path is the root
    # start from root
    if pathList[0]  == self.root.name:
      current = self.root
      pathList = pathList[1:]


    # handle impossible situations
    if current is None:
      print(f"PANIC: Cannot resolve path '{path}': null start")
    if not current.isDir:
      print(f"PANIC: Cannot resolve path '{path}': Path start '{current.name}' is not a directory")

    for i in range(len(pathList)):

      name = pathList[i]
      
      # empty, don't process
      if name == "": continue
      
      # pathing to current file, continue
      if name == ".":
        continue
      
      # path to parent
      # if parent is None, assume file is a root
      if name == "..":  
        if current.parent is not None:
          current = current.parent
        continue
      
      # if file along path is not a directory
      # return None
      if i < (len(pathList) - 1) and not current.isDir:
        print(f"{'ERROR' if caller == '' else caller}: Cannot resolve path '{path}': '{current.name}' is not a directory")
        return None

      # begin checking next element
      next = current.getFile(name)

      # Return None if file along path isn't found
      if next is None:
        print(f"{'ERROR' if caller == '' else caller}: Cannot resolve path '{path}': '{name}' not found")
        return None

      current = next

    return current

  def get(self, path: str, caller: str=''):
    return self.resolvePath(path.split("/"), caller=caller)

  def ls(self, path: str, recursive:bool = False, all:bool=False):
    f: File | None = self.resolvePath(path.split("/"), caller='ls')
    if f is None: return
    f.listFiles(all=all)

  def cd(self, path:str):
    f: File | None = self.resolvePath(path.split("/"))
    if f is None: return
    if not f.isDir:
      print(f"cd: {path} is a file, not a directory")
      return
    self.cwd = f

  def mkfile(self, path: str, isDir: bool=False) -> bool:
    # Creates a file in the specified path.
    pathList = path.split("/")
    tgt: File = self.resolvePath(pathList[:-1], caller='mkdir')
    if tgt is None: return False
    return tgt.createFile(pathList[-1], isDir) is not None
  
  def mkdir(self, path: str) -> bool:
    return self.mkfile(path, True)
  
  def rm(self, path: str, recursive:bool=False, caller:str='rm') -> bool:
    tgt: File | None = self.resolvePath(path.split("/"))
    if tgt is None: return False
    if tgt.parent is None:
      print(f"{caller}: cannot remove '{path}': Is root")
      return
    if tgt.isDir:
      if not recursive:
        print(f"{caller}: cannot remove '{path}': Is a directory")
        return False
      else:
        return tgt.parent.removeFile(tgt.name, True) is not None
    else:
      return tgt.parent.removeFile(tgt.name) is not None

  def mv(self, from_path: str, to_path: str, remove_source: bool=True) -> bool:
    # obtain file to move fromTarget
    # and its parent fromTargetParent
    fromTargetPathlist = from_path.split("/")
    fromTarget = self.resolvePath(fromTargetPathlist, caller='mv')
    fromTargetParent = fromTarget.parent
    if fromTarget is None:
      return False
    
    # obtain toTargetParent
    toTargetPathlist = to_path.split("/")
    toTargetParent:File | None = self.resolvePath(toTargetPathlist[:-1], caller='mv')
    if toTargetParent is None:
      return False
    
    # prepare rename or destination file in which to move fromTarget
    toTargetName = toTargetPathlist[-1]
    toTarget = toTargetParent.getFile(toTargetName)

    # case 1: destination exists, move in there
    if toTarget is not None:
      if toTarget.addFile(fromTarget if remove_source else deepcopy(fromTarget)):
        if remove_source: return fromTargetParent.removeFile(fromTarget.name, True) is not None
        else: return True
    
    # case 2: destination DNE, rename file
    else:
      
      # same parent, just rename
      if fromTargetParent == toTargetParent:
        if remove_source: return toTargetParent.renameFile(fromTarget.name, toTargetName)
        else: return toTargetParent.addFile(deepcopy(fromTarget))
      
      # different parent, move and rename
      elif toTargetParent.addFile(fromTarget if remove_source else deepcopy(fromTarget)):
        if remove_source: fromTargetParent.removeFile(fromTarget.name, True)
        return toTargetParent.renameFile(fromTarget.name, toTargetName)
      else:
        return False
      
  def cp(self, from_path: str, to_path: str) -> bool:
    return self.mv(from_path, to_path, remove_source=False)

  def rename(self, path: str, new_name: str) -> bool:
    tgt: File | None = self.resolvePath(path.split("/"), caller='rename')
    if tgt is None: return False
    tgt.rename(new_name)
    return True
  