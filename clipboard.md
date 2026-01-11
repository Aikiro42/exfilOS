```python
# Former Mollusk.run() code:

    # manual/help
    if (cmd.exec in ("help", "man")) or ("help" in cmd.wflags) or ("?" in cmd.lflags):
      print("There is no help.")

    # logout
    elif cmd.exec in ('quit', 'exit', 'logout'):
      print(color("Logging out...", bcolors.INFO))
      Mollusk.loadbar()
      self.stop()

    # clear
    elif cmd.exec in ("clear", "cls"):
      self.clear()
      
    # list directories
    elif cmd.exec in ("l", "ls"):
      self.ls(cmd)

    # change directory
    elif cmd.exec == "cd":
      if len(cmd.args) > 0:
        tgt = self.cwd.followPath(cmd.args[0], dirOnly=True)
        if tgt is not None:
          self.cwd = tgt
          self.cwdstr = self.cwd.tracePath()
      else:
        self.cwd = self.host.rootdir
        self.cwdstr = self.cwd.name
    
    # make directory
    elif cmd.exec == "mkdir":
      if len(cmd.args) > 0:
        print(cmd.args)
        self.host.fs.mkdir(cmd.args[0])
      else:
        print("ERROR: Path not specified")
    
    # make file
    elif cmd.exec in ("touch", "mkfile"):
      if len(cmd.args) > 0:
        self.cwd.touch(cmd.args[0])
      else:
        print("ERROR: File not specified")

    # code
    elif cmd.exec in ("edit", "code", "nano", "vim"):
      if len(cmd.args) > 0:
        self.cwd.edit(cmd.args[0])
      else:
        print("ERROR: File not specified")
    
    # view file
    elif cmd.exec in ("cat", "view", "read"):
      if len(cmd.args) > 0:
        self.cwd.read(cmd.args[0])
      else:
        print("ERROR: File not specified")
    
    # save progress
    elif cmd.exec in ("backup", "save", "savegame"):
      if Mollusk.loadbar(failChance=0.05):
        exportFiles(self.home.rootdir)
        print(color("Saved successfully!", bcolors.OK))
      else:
        print(color("Save Failed!", bcolors.ERROR))
    
    elif cmd.exec in ("restart", "reload", "loadgame"):
      print(color("RESTARTING GAME...", bcolors.WARNING))
      Mollusk.loadbar()
      self.clear()

    # timer
    elif cmd.exec == "timer":
      if len(cmd.args) <= 0:
        print("ERROR: No duration or timer name specified")
      else:
        duration = 0
        try:
          duration = int(cmd.args[0])
          self.startTimer("default", duration)
        except:
          if len(cmd.args) == 1:
            self.checkTimer(cmd.args[0])
          else:
            try:
              duration = int(cmd.args[1])
              self.startTimer(cmd.args[0], duration)
            except: print("ERROR: Invalid Duration")

    # view cache
    elif cmd.exec in ("backpack", "cache"):
      self.showCache()

    # download file to cache
    elif cmd.exec in ("dl", "download", "wget", "curl"):
      self.download(cmd)

    # blank
    elif cmd.exec == "": pass
    
    # unknown
    else:
      print(f"ERROR: No command found with name \"{cmd.cmdstr}\"")

```