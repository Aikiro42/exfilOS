from core.file import File, Dir, Link
from core.colors import color
from core.const import bcolors

class Host:
  def __init__(self, name:str, capacity=-1):
    self.name = name
    self.root = Dir('', capacity=capacity)
    
    self.mountPoint = Dir('mnt')
    self.root.addFile(self.mountPoint, caller="Host.__init__")
    
    self.home = Dir('home')
    self.root.addFile(self.home, caller="Host.__init__")
    
  @staticmethod
  def parsePath(path: str) -> list[str]:
    if path == '': return []
    if path == '/': return ['']
    return path.split("/")

  def mount(self, root: Dir):
    # root.parent -> mountPoint
    uplink = Link('mnt', self.mountPoint)
    self.root.parent = uplink

    # 'mnt/<root.name>' -> root
    downlink = Link(self.root.name, self.root)
    self.mountPoint.addFile(downlink)
  
  def unmount(self, rootname: str) -> Dir | None:
    downlink: Link = self.mountPoint.removeFile(rootname)
    if downlink is None: return None
    root = downlink.data
    root.parent = None

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


    