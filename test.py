class A:
  def __init__(self):
    self.a = 1

class B(A):
  def __init__(self):
    self.a = 2


x = B()

print(type(x) is B)