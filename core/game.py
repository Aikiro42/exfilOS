from core.shell import Mollusk
from core.host import Host, LOCALHOST
from core.file import importFiles, File, ROOT_NAME

class Player:
  def __init__(self, name="player"):
    self.name = name
    self.money = 0
    self.gems = 0
    self.health = 100
    self.maxHealth = 100
    try:
      self.home = Host("localhost", importFiles())
    except:
      self.home = Host("localhost", File(ROOT_NAME, True))
    self.shell = Mollusk(self.name, self.home)