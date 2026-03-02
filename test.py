from core.shell import Command

import re

cases = [
  'python `C:/Program Files/main.py`'
  "dwa -1",
  "haha - -- - -- 'whdahdwahdhawgvhaeg fhrsuighdrg'",
  "--hello",
  "adad -",
  "tisro -shit69",
  "-shit",
  "dwdwd --shit",
  "test -eusi `d w au ha` 'ghsr uigi' \"ghr igrg didgd\" rfsf rgr"
]

for case in cases:
  valid = Command.parse(case)
  print(f"{case}")
  if valid:
    print(f"  exec: \t{valid.exec}")
    print(f"  args: \t{valid.args}")
    print(f"  flags: \t{valid.flags}")
  print()