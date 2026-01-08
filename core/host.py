from core.file import File, ROOT

class Host:
  def __init__(self, name:str, root: File):
    self.name = name
    self.rootdir = root

LOCALHOST = Host("localhost", ROOT)