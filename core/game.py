from core.shell import Mollusk
from core.host import Host
from core.file import File, ROOT_NAME

class Player:
  def __init__(self, name="guest", savedFileSystem:str="filesys.json"):
    self.name = name
    self.load(savedFileSystem)
  
  def load(self, savedFileSystem:str="filesys.json"):
    self.money = 0
    self.gems = 0
    self.health = 100
    self.maxHealth = 100
    try:
      self.home = Host("localhost", File.fromJson(savedFileSystem))
    except:
      self.home = Host("localhost", File(ROOT_NAME, True))
    self.shell = Mollusk(self.name, self.home)