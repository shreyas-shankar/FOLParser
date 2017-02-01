class Literal:

    def __init__(self,a,b,c):
        self.predicate = a
        self.values = b
        self.type = c

    def __str__(self):
        return "%s(%s)" % (self.predicate, self.values)
