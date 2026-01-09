import json
from typing import Dict
from .const import *
from .colors import color
from copy import deepcopy

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

  def ls(self, path: str, recursive:bool = False, all:bool=False):
    f: File | None = self.resolvePath(path.split("/"), caller='ls')
    if f is None: return
    f.ls(path, recursive=recursive, all=all, root=self.root)

  def cd(self, path:str):
    f: File | None = self.resolvePath(path)
    if f is None: return
    if not f.isDir:
      print(f"cd: {path} is a file, not a directory")
      return
    self.cwd = f

  def mkfile(self, path: str, isDir: bool=False):
    # Creates a file in the specified path.
    pathList = path.split("/")
    tgt: File = self.resolvePath(pathList[:-1], caller='mkdir')
    if tgt is None: return False
    return tgt.createFile(pathList[-1], isDir) is not None
  
  def mkdir(self, path: str) -> bool:
    return self.mkfile(path, True)
  
  def rm(self, path: str, recursive:bool=False) -> bool:
    tgt: File | None = self.resolvePath(path)
    if tgt is None: return False
    if tgt.isDir:
      if not recursive:
        print(f"rm: cannot remove '{path}': Is a directory")
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

  def rename(self, old_name, new_name) -> bool:
    ...


class File:
  def __init__(self, name:str, isDir:bool, data:str|Dict[str, File]="", parent:File|None=None, root:File|None=None):
    self.isDir = isDir
    self.name = name
    self.parent = parent
    if root is None:
      self.root = self
    self.data = {} if isDir else data
  
  @property
  def path(self):
    if self.parent is None: return self.name
    return f"{self.parent.path}/{self.name}"

  def validateFiles(self):
    # Makes sure that all the keys in the directory's data
    # correspond with the name of the file they refer to.
    if not self.isDir: return
    for filename, file in self.data.items():
      if file.name != filename:
        self.data[file.name] = self.data.pop(filename)
  
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
      print(f"ERROR: {name} does not exist")
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

  def edit(self, path:str):
    if not self.isDir:
      print(f"ERROR: No files inside file {self.name}???")
      return
    
    pathlist = path.split("/")
    dirpath = "/".join(pathlist[:-1])
    tgt = self.followPath(dirpath)

    if tgt is None:
      print(f"ERROR: tgt is none???")
      return
    
    file = pathlist[-1]

    if file not in tgt.data.keys(): # type: ignore
      tgt.touch(file)
    
    tgt = tgt.getFile(file)
    if tgt is None:
      print(f"ERROR: tgt is none 2???")
      return

    new_data = ""

    print("Press Ctrl+D to finish input.")
    while True:
      try:
        new_data += input()
      except:
        break
    
    tgt.data = new_data
    
  # dir operation
  # lists all files within
  def ls(self, path:str="", recursive:bool=False, all:bool=False, level:int=0):
    if not self.isDir:
      print(f"ERROR: Cannot ls inside {self.name}")
      return
    tgt = self
    if path != "":
      tgt = self.followPath(path)
      if tgt is None:
        return

    for filename, file in tgt.data.items(): # type: ignore
      if filename[0] == '.' and not all: continue  # skip hidden files
      print(f"{'  '*level}{color(file.name, bcolors.DIR) if file.isDir else file.name}")
      if recursive and MAX_LS_RECRSION > level + 1:
        file.ls(recursive=True, all=all, level=level+1)  # won't ls if file

  # dir operation
  # creates a file/directory with filename `name`
  # isDir dictates if created is file or directory
  def touch(self, name: str, isDir: bool=False):
    if not self.isDir:
      print(f"ERROR: cannot make file within {self.name}, is file")
      return
    self.data[name] = File(name, isDir, parent=self, root=self.root) # type: ignore
  
  def read(self, path:str, root:File=None):
    if not self.isDir:
      print(f"ERROR: Cannot retrieve file from {self.name}, is file")
      return
    tgt:File | None = self.followPath(path)
    if tgt is None: return
    if tgt.isDir:
      print(f"ERROR: Cannot read {self.name}, is dir")
      return
    print(tgt.data)
    
  # dir operation
  # Follows path starting from self
  # Returns the final file in the path
  def followPath(self, path: str, dirOnly:bool=False) -> File | None:
    current: File = self
    
    if not current.isDir:
      print("ERROR: Cannot follow path from file")
      return None
    
    pathList: list[str] = path.split("/")
    for i in range(len(pathList)):

      name = pathList[i]

      if name == "": continue  # empty, don't process
      
      if name == self.root.name:  # goto root
        if self.root is None:
          print("ERROR: No root specified")
          return None
        current = self.root
        continue
      
      if name == "..":  # goto parent
        if current.parent is not None:
          current = current.parent
        continue
    
      if name == ".":  # current
        continue

      current = current.getFile(name)
      if current is None:
        # error already thrown by getFile
        break
      if dirOnly and not current.isDir:
        print("ERROR: Attempted to follow path into file.")
        return None

    return current
  
  # returns the string path to the file
  def tracePath(self) -> str:
    path = f"{self.name}"
    tgt = self.parent
    while tgt is not None:
      path = f"{tgt.name}/{path}"
      tgt = tgt.parent
    return path
  
  # dir operation
  # removes file from dir
  def rm(self, path:str):
    if not self.isDir:
      print(f"ERROR: {self.name} is not dir")
      return
    
    rmfile = self.getFile(path)
    if rmfile is None:
      # error already thrown by getfile
      return
    if rmfile.isDir:
      # use rmdir to remove directories
      print(f"ERROR: Cannot remove dir {rmfile.name}")
      return
    
    del self.data[rmfile.name]
  
  # dir operation
  # removes directory
  def rmdir(self, path:str, recursive:bool=False):
    if not self.isDir:
      print(f"ERROR: {self.name} is not dir")
      return
    
    rmtgt = self.followPath(path)
    if rmtgt == None:
      # error already thrown by followPath
      return
    
    # target found
    # throw error if target is file or nonempty
    # otherwise, if file is nonempty but removal is recursive
    # recursively remove all files within
    if not rmtgt.isDir:
      print(f"ERROR: {rmtgt.name} is not dir")
    if len(rmtgt.data) > 0:
      if not recursive:
        print(f"ERROR: {rmtgt.name} is not empty")
      else:
        for filename, file in rmtgt.data.items():
          if file.isDir:
            rmtgt.rmdir(filename)
          else:
            rmtgt.rm(filename)
    
    # remove directory
    del self.data[rmtgt.name]

  def JSON(self):
    pass  # TODO: JSONify

  def mkdir(self, name):
    self.touch(name, isDir=True)

def processExport(filetree:File) -> dict | str:
  if not filetree.isDir:
    return filetree.data
  
  root = {}
  for filename, file in filetree.data.items():
    if filename == "." or filename == "..": continue
    root[filename]  = processExport(file)

  return root

def processImport(obj: dict, name:str=ROOT_NAME, level=0) -> File:
  root = File(name, True)
  for filename, filedata in obj.items():
    # print(f"{"  "*(level)}{filename}: ({type(filedata)}) {filedata}")
    if type(filedata) == str:
      root.touch(filename)
      root.getFile(filename).data = filedata
    else:
      root.data[filename] = processImport(filedata, name=filename, level=level+1)
      root.getFile(filename).parent = root
  
  return root

def exportFiles(filetree:File, exportFile="filesys.json"):
  with open(exportFile, "w") as f:
    f.write(json.dumps(processExport(filetree)))

def importFiles(importFile:str="filesys.json") -> File:
  with open(importFile) as f:
    return processImport(json.loads(f.read()))

try:
  ROOT = importFiles()
except:
  ROOT = File(ROOT_NAME, True)