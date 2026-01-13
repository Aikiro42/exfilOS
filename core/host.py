from core.file import File, FileSystem

class Host:
  def __init__(self, name:str, root: File | None = None):
    self.name = name
    self._fs_ = FileSystem(root)
    self.currentfs = self._fs_
    self.mounted = {
      self._fs_.name: self._fs_
    }

  @property
  def fs(self):
    return self.currentfs
  
  def resolvePath(self, cwd: File, path:str) -> File | None:
    pathlist = path.split("/")
    if len(pathlist) == 0: return cwd
    
    current = cwd
    step = 0

    if pathlist[0] == self.fs.root.name:
      current = self.fs.root
      step = 1

    while step < pathlist and current is not None:
      nextname = pathlist[step]
      
      if nextname == ".":
        continue

      if nextname == "..":
        if current.parent is None:
          continue
        current = current.parent
        continue

      current = current.getFile(nextname)
      step += 1

    return current
  
  def listFileSystems(self) -> list[(str, int, int)]:
    return [(fsname, fs.size, fs.capacity) for fsname, fs in self.mounted.items()]

  def mount(self, fs: FileSystem | File, caller='Host.mount') -> FileSystem:
    
    if self.mounted.get(fs.name, None) is not None:
      print(f"{caller}: Cannot mount '{fs.name}': FileSystem with same name already mounted")
      return None
    
    tofs = fs
    if issubclass(type(fs), File):
      tofs = FileSystem(fs)

    self.mounted[fs.name] = tofs

    return tofs
  
  def switch(self, fs: str | FileSystem | File | None, unmount:bool=False, caller='Host.switch') -> bool:
    
    tofs = None
    
    if fs is None:
      tofs = self._fs_
    
    elif (type(fs) is FileSystem) or issubclass(type(fs), File):
      tofs = self.mount(fs, caller='Host.switch')
      if tofs is None:
        return False
      
    elif type(fs) is str:
      tofs = self.mounted.get(fs, None)
      if tofs is None:
        print(f"{caller}: Cannot switch to {fs}: not mounted")
        return False

    self.currentfs = tofs

    # FIXME: unsafe

    return True
    
  
  def unmount(self, rootname: str, caller='Host.unmount'):
    umfs = self.mounted.get(rootname, None)
    if umfs is None:
      print(f"{caller}: Cannot unmount '{rootname}': not mounted")
      return

    if umfs == self._fs_:
      print(f"{caller}: Cannot unmount '{rootname}': is default")
      return
    
    del self.mounted[rootname]
    
    