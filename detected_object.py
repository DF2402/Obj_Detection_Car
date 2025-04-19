class obj:
<<<<<<< HEAD
=======
    # This class is used to create an object with a name, size, and position.
    # The size is a tuple containing the width and height of the object.
    # cx is the distance the center x of the object.
>>>>>>> d32c241 (final code)
    def __init__(self,name,size,x,y):
        self.s = size
        self.n = name
        self.x = x
        self.y = y
        self.area = self.s[0]*self.s[1]
        self.cx = self.x - 1280/2
    def __str__(self):
        return f"n :{self.n}, area :{self.area},cx :{self.cx}, x :{self.x},y:{self.y}"
    
    
        
