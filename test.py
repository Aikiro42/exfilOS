import re

cases = [
  "-1",
  "-",
  "--hello",
  "-",
  "-shit69",
  "-shit",
  "--shit"
]


for case in cases:
  print(f"{case:10} -> {re.fullmatch(r'(-|--)[a-zA-Z]+', case) is not None}")