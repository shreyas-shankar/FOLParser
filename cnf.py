class SimplificationTree:

    def __init__(self,a,b,c,d):
        self.op = b
        self.left = a
        self.right = c
        self.type = d

    # def __str__(self):
    #     return (self.left + self.op + self.right)
