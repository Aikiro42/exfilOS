from core.shell import Mollusk
from core.host import Host, LOCALHOST

class Player:
  def __init__(self, name="player"):
    self.name = name
    self.money = 0
    self.gems = 0
    self.health = 100
    self.maxHealth = 100

    self.home = LOCALHOST
    self.shell = Mollusk(self.name, self.home)