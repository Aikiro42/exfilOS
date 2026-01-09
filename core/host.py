from core.file import File, FileSystem, ROOT

class Host:
  def __init__(self, name:str, root: File | None = None):
    self.name = name
    self.fs = FileSystem(root)

LOCALHOST = Host("localhost", ROOT)