class obj:
    def __init__(self,name,size,x,y):
        self.s = size
        self.n = name
        self.x = x
        self.y = y
        self.area = self.s[0]*self.s[1]
        self.cx = self.x - 1280/2
    def __str__(self):
        return f"n :{self.n}, area :{self.area},cx :{self.cx}, x :{self.x},y:{self.y}"
    
    
        
