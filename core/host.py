from core.file import File, Dir, Link, FileSystem
import json
from pathlib import Path

class Host:
  def __init__(self, name:str, capacity=-1):
    self.name = name
    self._fs_: FileSystem = FileSystem(capacity)
    self._linked_hosts_ = {}

  @property
  def fs(self):
    return self._fs_

  def updateCapacity(self, new_capacity: int):
    """
    Updates the capacity of this host's filesystem.
    
    The new capacity must be bigger than the current capacity.
    """
    self._fs_.capacity = new_capacity
  
  def link(self, host: Host) -> bool:
    """
    Links a host to this host, allowing traversal between them.
    """
    if not host.link(self): return False
    if self._linked_hosts_.get(host.name, None) is not None: return False
    self._linked_hosts_[host.name] = host
    return True
  
  def unlink(self, host: Host | str, force:bool=False) -> bool:
    """
    Unlinks a host from this host.

    If `force` is true, attempts
    """
    if force:
      try:
        # attempt to unlink
        if isinstance(host, Host):
          host.unlink(self, force=True)
        else:
          self._linked_hosts_[host].unlink(self, force=True)
      except:
        ...
      finally:
        del self._linked_hosts_[host.name if isinstance(host, Host) else host]
      return True
    
    if isinstance(host, Host):
      if not host.unlink(self): return False
      del self._linked_hosts_[host.name]
    
    else:
      tgt = self._linked_hosts_[host]
      if not tgt.unlink(self): return False
      del self._linked_hosts_[host]
    
    return True

  def save(self, jsonpath: str = "savedata/default/filesys.json") -> bool:
    """
    Saves the file system of the host into a JSON file specified by the path. Returns `True` if successful.
    """
    try:
      output_file = Path(jsonpath)
      output_file.parent.mkdir(exist_ok=True, parents=True)
      with open(jsonpath, "w") as savefile:
        savefile.write(json.dumps(self._fs_.to_json()))
      return True
    except:
      return False

  def load(self, jsonpath: str = "savedata/default/filesys.json") -> bool:
    """
    Loads a file system from a JSON file. Returns `True` if successful.
    """
    savestr: str
    with open(jsonpath, "w") as savefile:
      savestr = savefile.read()
    
    saveJSON: dict = json.loads(savestr)
    
    loadedFS: FileSystem | None = FileSystem.from_json(saveJSON)
    if loadedFS is None: return False
    self._fs_ = loadedFS 
    return True