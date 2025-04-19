import process
import math 
import pandas as pd
class aim_process(process.process):
    def __init__(self):
        super().__init__()

<<<<<<< HEAD
    def run(self,area,cx,parameters):
=======
    
    def run(self,area,cx,parameters):
        # this function is used to calculate the left and right output speed of the robot based on the area and cx value.
        # cx is the distance from center x coordinate of the object, which is used to determine the direction of the robot's movement.
        # area is the area of the object, which is used to determine the speed of the robot.
        # parameters is a tuple containing the following values:
        # diff_speed_limit: the maximum speed difference between the left and right wheels of the robot.
        # left_ratio: the ratio of the left wheel speed to the maximum speed of the robot.
        # right_ratio: the ratio of the right wheel speed to the maximum speed of the robot.
        # base_speed: the base speed of the robot.
>>>>>>> d32c241 (final code)

        left_ouput, right_ouput = (0,0)
        
        diff_speed_limit,left_ratio,right_ratio, base_speed,base_speed_limit,slow_ratio = parameters
        
        diff_speed = cx/640 * diff_speed_limit
        
        # when the ball at left , cx < 0，and right ratio need to be oppsite  
        right_ratio *= -1
<<<<<<< HEAD
        """
        if area <= 160000:
            forward_speed = base_speed_limit
        elif area < 202500 and area > 160000 :
            forward_speed = base_speed_limit / (area / 202500 * slow_ratio) 
        else:
            forward_speed = base_speed
        """   
=======
>>>>>>> d32c241 (final code)

        forward_speed = base_speed
        left_ouput  = min(int(diff_speed * left_ratio  + forward_speed ) ,100)

        right_ouput = min(int(diff_speed * right_ratio + forward_speed ) ,100)

        return (left_ouput, right_ouput)
<<<<<<< HEAD
    
=======
    # this function is used to calculate the left and right output speed of the robot based on the area and cx value.
>>>>>>> d32c241 (final code)
    def test(self, run_test_set_path, change_test_set_path, run_parameters,decision_parameters, left_bias=0, right_bias=0):
        print('aim_process run() unit test')
        df = pd.read_csv(run_test_set_path)
        #print(df)
        cnt_pass = 0
        cnt_fail = 0
        for index, row in df.iterrows():
            area = int(row['area'])
            cx = int(row['cx'])
            ctrl = row['ctrl']
            #print(index, area, cx, ctrl)

            left_ouput, right_ouput = self.run(area,cx,run_parameters)
            
            left_ouput = left_ouput - left_bias 
            right_ouput = right_ouput - right_bias 

            output = None
            if (left_ouput<0 and right_ouput< 0 ):
                output = "back"
            elif (left_ouput-right_ouput > 0 ):
                output = "right"
            elif (left_ouput-right_ouput < 0 ):
                output = "left"
            elif (left_ouput == 100 and right_ouput == 100 ):
                output = "shoot"    
            else:
                output = "forward"
            if output == ctrl:
                cnt_pass +=1
                #print(row,output,(left_ouput, right_ouput))
            else:
                cnt_fail +=1
                print(row,output,(left_ouput, right_ouput))
                
        print(f"pass:{cnt_pass}, fail:{cnt_fail}")

        print('aim_process change() unit test')
        df = pd.read_csv(change_test_set_path)
        #print(df)
        cnt_pass = 0
        cnt_fail = 0
        for index, row in df.iterrows():
            area = int(row['area'])
            cx = int(row['cx'])
            ctrl = row['ctrl']
            #print(index, area, cx, ctrl)

            State= self.state_change(area,cx,decision_parameters)
           
            if State == ctrl:
                cnt_pass +=1
                #print(row,output,(left_ouput, right_ouput))
            else:
                cnt_fail +=1
                print(row,output,(left_ouput, right_ouput))
                
        print(f"pass:{cnt_pass}, fail:{cnt_fail}")
        
    
    def state_change(self,area,cx,parameters=(302500,250)):
        decision_area, decision_dcx = parameters
        cx = abs(cx)
        if (decision_area <= area and decision_dcx >= cx ):
            return True
        return False
        
if __name__ == '__main__':
    diff_speed_limit = 50
    left_ratio = 0.5
    right_ratio = 0.5
    base_speed = 10
    base_speed_limit = 50
    slow_ratio = 2
    run_parameters = (diff_speed_limit,left_ratio,right_ratio, base_speed,base_speed_limit,slow_ratio)
    decision_area = 550*550
    decision_dcx = 250
    decision_parameters = (decision_area,decision_dcx)
    aim_process = aim_process()
    aim_process.test('./23Mar/aim_run_case.csv','./23Mar/aim_change_case.csv',run_parameters,decision_parameters,left_bias=0,right_bias=0)