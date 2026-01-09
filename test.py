class Apple:
  def __init__(self):
    self.flavor = "sweet"
  
  def foo(self):
    x, y = input("What? ").split(" ")
    eval(f"self.{x}(y)")

  def hello(self, x):
    print(f"{x} is my world!")


a = Apple()
a.foo()