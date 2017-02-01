class kbObject:
    def __init__(self, p, v, n):
      self.predicate = p
      self.values = v
      self.n = n

    def __str__(self):
        if self.n == "Y":
            return "~" + str(self.predicate) + str(self.values) + " "
        else:
            return str(self.predicate) + str(self.values) + " "

    def __repr__(self):
       if self.n == "Y":
           return "~" + str(self.predicate) + str(self.values) + " "
       else:
           return str(self.predicate) + str(self.values) + " "
