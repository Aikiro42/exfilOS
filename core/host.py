from core.file import File

class Host:
  def __init__(self, name:str, root: File):
    self.name = name
    self.rootdir = File