from core.file import *
"""
y = None
print("y = None\n")
print(f"y is File : {y is File}")
print(f"y is Dir : {y is Dir}")
print(f"y is None : {y is None}")
print(f"type(y) is File : {type(y) is File}")
print(f"type(y) is Dir : {type(y) is Dir}")
print(f"type(y) is None : {type(y) is None}")
print(f"type(y) == File : {type(y) == File}")
print(f"type(y) == Dir : {type(y) == Dir}")
print(f"type(y) == None : {type(y) == None}")
print(f"isinstance(y, File) == {isinstance(y, File)}")
print(f"isinstance(y, Dir) == {isinstance(y, Dir)}")
print(f"isinstance(y, None) == ERROR")
"""

def parsePath(path: str) -> list[str]:
  if path == '': return []
  if path == '/': return ['']
  return path.split("/")

try:
  while True:
    x = input(f"$ ")
    print(parsePath(x))
except:
  print()