import pandas as pd
<<<<<<< HEAD
=======
# This is a base class for process handling
# It is designed to be inherited by other classes that implement specific process logic.
>>>>>>> d32c241 (final code)
class process:
    def __init__(self):
        pass

    def test(self,test_set_path,parameters,left_bias=0,right_bias=0):
        
        df = pd.read_csv(test_set_path)
        
        cnt_pass = 0
        cnt_fail = 0
        for case in df:
            area,cx = (case[1],case[2])
            left_ouput, right_ouput = self.run(area,cx,parameters)
            
            left_ouput = left_ouput - left_bias 
            right_ouput = right_ouput - right_bias 

            output = None
            if (left_ouput<0 and right_ouput< 0 ):
                output = "back"
            elif (left_ouput-right_ouput> 0 ):
                output = "right"
            elif (left_ouput-right_ouput< 0 ):
                output = "left"
            elif (left_ouput == 100 and right_ouput == 100 ):
                output = "shoot"    
            else:
                output = "forward"
            if output == case[3]:
                cnt_pass +=1
                print(case,output,(left_ouput, right_ouput))
            else:
                cnt_fail +=1
                print(case,output,(left_ouput, right_ouput))
                
            print(f"pass:{cnt_pass}, fail:{cnt_fail}")
    def run(self,area,cx,parameters):
        pass