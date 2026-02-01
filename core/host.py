from core.file import File, Dir, Link, FileSystem

class Host:
  def __init__(self, name:str, capacity=-1):
    self.name = name
    self.fs: FileSystem = FileSystem(capacity=capacity)
    
    self.mountPoint = Dir('mnt')
    self.fs.root.addFile(self.mountPoint, caller="Host.__init__")
    
    self.home = Dir('home')
    self.fs.root.addFile(self.home, caller="Host.__init__")
    
  @staticmethod
  def parsePath(path: str) -> list[str]:
    parsed = path.split("/")

    # parse backslashes
    parsebs = []
    for x in parsed:
      parsebs += x.split("\\")
    parsed = parsebs
    
    # remove duplicate slashes and current dirs
    parsed = parsed[0] + [x for x in parsed[1:] if len(x) > 0 and x != "."]
    return parsed

  def mount(self, root: Dir): ...  # add a Link in self.mountPoint that links to a root, set root's parent to a Link
  def unmount(self, rootname: str) -> Dir | None: ...  # re

  def resolvePath(self, cwd: Dir, pathlist: list[str]) -> File | None:
    current = cwd
    step = 0
    if pathlist[0] == '':
      current = self.root
      step = 1
    
    end = len(pathlist)

    while step <= end:
      nextname = pathlist[step]
      if nextname == '.':
        pass

      elif nextname == '..':
        if current.parent is not None:
          current = current.parent
      
      else:
        next = current.getFile(nextname)
        if type(next) is Link:
          next = next.data
        if type(next) is File and step < end:
          return None
        current = next
      
      step += 1

    return current

    