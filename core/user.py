from core.file import File, Cache

class User:
  
  def __init__(self, name: str, savepath: str=""):
    self.name = name
    self.savepath = savepath
    if savepath == "":
      self.savepath = f"savedata/{self.name}"
    self.load()
  
  def load(self):
    self.money = 0
    self.gems = 0
    self.health = 100
    self.maxHealth = 100
    self.cache = Cache()
    try:
      cacheFile = File.fromJson(jsonPath=f"{self.savepath}/cache.json")
      self.cache.fromFile(cacheFile)
    except:
      pass