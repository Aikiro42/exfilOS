import json
from .const import *
from .colors import color

class File:
  def __init__(self, name:str, isDir:bool, data:str="", parent:File=None, root:File=None):
    self.isDir = isDir
    self.name = name
    self.parent = parent
    if root is None:
      self.root = self
    self.data = {".": self, "..": parent} if isDir else data

  def edit(self, path:str):
    if not self.isDir:
      print(f"ERROR: No files inside file {self.name}")
      return
    
    pathlist = path.split("/")
    dirpath = "/".join(pathlist[:-1])
    tgt = self.followPath(dirpath)
    file = pathlist[-1]

    if file not in tgt.data.keys():
      tgt.touch(file)
    
    tgt = tgt.getFile(file)
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
  def ls(self, recursive:bool=False, all:bool=False, path:str="", root:File=None, level:int=0):
    if not self.isDir:
      print(f"ERROR: Cannot ls inside {self.name}")
      return
    tgt = self
    if path != "":
      tgt = self.followPath(path)
      if tgt is None:
        return

    for filename, file in tgt.data.items():
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
    self.data[name] = File(name, isDir, parent=self, root=self.root)
  
  # dir operation
  # returns file with filename `name` within itself
  # returns None if file is nonexistent
  def getFile(self, name: str) -> File | None:
    if not self.isDir:
      print(f"ERROR: Cannot retrieve file from {self.name}, is file")
      return None
    if name not in self.data.keys():
      print(f"ERROR: {name} does not exist")
      return None
    return self.data[name]
  
  def read(self, path:str, root:File=None):
    if not self.isDir:
      print(f"ERROR: Cannot retrieve file from {self.name}, is file")
      return
    tgt:File = self.followPath(path)
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