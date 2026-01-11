from core.file import File, FileSystem

class Host:
  def __init__(self, name:str, root: File | None = None):
    self.name = name
    self.fs = FileSystem(root)
    