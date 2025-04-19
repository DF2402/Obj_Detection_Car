import catch_process
import aim_process
import math 
import pandas as pd
import detected_object
import supporting_aim_process

import cv2
import torch
import numpy as np
import math
import time
import serial
import random
import pandas as pd
import time
from test_vision import visualizer

# Parameters for decision making
decision_sx = 290
decision_dcx = 45
catch_process_decision_parameters = (decision_sx,decision_dcx)

decision_area = 120000
decision_dcx = 100
aim_process_decision_parameters =  (decision_area,decision_dcx)


decision_area = 200000
decision_dcx = 150
blue_gate_aim_process_decision_parameters =  (decision_area,decision_dcx)

decision_area = 270000
decision_dcx = 200
blue_gate_shoot_process_decision_parameters =  (decision_area,decision_dcx)

decision_area = 260000
decision_dcx = 250
shoot_process_decision_parameters =  (decision_area,decision_dcx)

# Parameters for car control 
diff_speed_limit = 50
left_ratio = 0.55
right_ratio = 0.45
base_speed = 35
base_speed_limit = 35
slow_ratio = 2.75
catch_process_run_parameters = (diff_speed_limit,left_ratio,right_ratio, base_speed,base_speed_limit,slow_ratio)

diff_speed_limit = 50
left_ratio = 0.3
right_ratio = 0.15
base_speed = 35
base_speed_limit = 35
slow_ratio = 2
aim_process_run_parameters = (diff_speed_limit,left_ratio,right_ratio, base_speed,base_speed_limit,slow_ratio)

diff_speed_limit = 37
left_ratio = 0.25
right_ratio = 0.15
base_speed = 35
base_speed_limit = 35
slow_ratio = 2
white_gate_aim_process_run_parameters = (diff_speed_limit,left_ratio,right_ratio, base_speed,base_speed_limit,slow_ratio)

diff_speed_limit = 80
left_ratio = 0.65
right_ratio = 0.55
base_speed = 31
base_speed_limit = 31
slow_ratio = 2
supporting_aim_process_run_parameters = (diff_speed_limit,left_ratio,right_ratio, base_speed,base_speed_limit,slow_ratio)

diff_speed_limit = 60
left_ratio = 0.35
right_ratio = 0.25
base_speed = 31
base_speed_limit = 31
slow_ratio = 2
white_gate_supporting_aim_process_run_parameters = (diff_speed_limit,left_ratio,right_ratio, base_speed,base_speed_limit,slow_ratio)

# Function to determine the sign of an integer
# This function returns '-' if the integer is negative and '+' if it is non-negative.
def sign(int_input):
            return '-' if int_input < 0 else '+'

# Function to display information on the frame
def display(frame,obj,state,obj_color,power):
     left_power,right_power = power
     cv2.putText(frame,f"{obj.n}:{obj.area} {obj.cx}"  ,(200, 40),cv2.FONT_HERSHEY_SIMPLEX,0.5,obj_color,2,)
     cv2.putText(frame,f"approching {obj.n}"  ,(200, 60),cv2.FONT_HERSHEY_SIMPLEX,0.5,obj_color,2,)
     cv2.putText(frame,f"power: {left_power,right_power}"  ,(200, 80),cv2.FONT_HERSHEY_SIMPLEX,0.5,obj_color,2,)
     cv2.putText(frame,f"state: {state}"  ,(200, 100),cv2.FONT_HERSHEY_SIMPLEX,0.5,obj_color,2,)
        
# Function to define the color of the object based on its name
# This function returns a tuple representing the RGB color for the object.
def define_obj_color(obj):
    if obj.n == 'ball_red':
        obj_color = (255,0,0)
    elif obj.n == 'ball_green':
        obj_color= (0,255,0)
    elif obj.n == 'gate_orange':
        obj_color= (235, 119, 52)
    elif obj.n == 'gate_white':
        obj_color= (255,255,255)
    else:
        obj_color= (0,0,255)
    return obj_color
            
class main_process():
    # Initialize the main process with the model path
    # This function sets up the UART connection and loads the YOLOv5 model.
    def __init__(self,model_path):
        uart_port = '/dev/ttyTHS0'  # Replace with the correct UART port (e.g., ttyTHS1, ttyTHS2)
        baud_rate = 115200          # Baud rahhhhte (e.g., 9600, 115200)
        timeout = 1                 # Timeout for reading in seconds
        
        try:
            self.ser = serial.Serial(
                port=uart_port,
                baudrate=baud_rate,
                timeout=timeout
            )
            print(f"Connected to {uart_port} with baud rate {baud_rate}")
        except Exception as e:
            print(f"Error opening UART: {e}")
            #exit()
        
        # Load the YOLOv5 model
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=True)
        # Set the webcam source
        webcam_source = 0 
        # Open the webcam
        self.cap = cv2.VideoCapture(webcam_source)
        # Set webcam resolution (optional)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # Check if webcam is opened successfully
        if not self.cap.isOpened():
            print("Error: Could not open webcam.")
            exit()
        print("Starting webcam... Press 'q' to quit.")

        self.catch_process = catch_process.catch_process()
        self.aim_process = supporting_aim_process.aim_process()
        self.state = 'init'
        self.catching = None
        self.supporting_aim_process = supporting_aim_process.aim_process()
        # Initialize lst for log
        self.gate_white = []
        self.gate_blue = []
        self.ball_red = []
        self.ball_green = []
        self.ball_orange = []
        self.ball_blue = []
        self.log = []
        self.cnt = 0

    # Function to send data over UART
    def send_data(self,data):
        
        if self.ser.isOpen():
            self.ser.write(data.encode())  # Convert string to bytes and send
            print(f"UART Command : {data}")
        else:
            print("UART port is not open!")
        
        #print(data)
    
    def run(self):
        tick = 0
        # Main loop for processing frames from the webcam
        # This loop captures frames, performs object detection, and controls the robot based on detected objects.
        while True:
            tick +=1
            
            log_list = [self.gate_white,self.gate_blue,self.ball_red,self.ball_blue,self.ball_green,self.ball_orange]

            # Read a frame from the webcam
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Could not read frame from webcam.")
                break

            # Draw vertical lines on the frame to set up the hook
            cv2.line(frame, (450, 0) , (450, 720) , (0,255,0), 2)
            cv2.line(frame, (830, 0) , (830, 720), (0,255,0), 2)

            # Convert the frame to RGB (YOLOv5 expects RGB input)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Perform inference
            results = self.model(frame_rgb)

            # Parse detection results and plot them directly on the frame
            detections = results.pandas().xyxy[0]  # Get the detections as a Pandas DataFrame
            m_Number_Object_01 = len(detections)
            obj_lst = [] 
            
            
            if(0<m_Number_Object_01):
                obj_lst,frame = self.detect_obj(detections,frame,tick)
                gate_white_missing  = True
                gate_blue_missing  = True

                
                for obj in obj_lst:
                    
                    if obj.n == "gate_white":
                        gate_white_missing  = False
                    if obj.n == "gate_blue":
                        gate_blue_missing  = False
                    if obj.n == "gate_orange":
                        orange_gate = obj

                #print(obj_lst)
                if self.state == 'a':
                    if(self.catching == 'g' or self.catching == 'r' or self.catching == 'b') and gate_white_missing:
                        # turn right if the car try to trace the white gate
                        left_power,right_power = self.supporting_aim_process.run(area=16000,cx=0,parameters=white_gate_supporting_aim_process_run_parameters,offset = 500)
                        self.send_data(f'[{sign(left_power)},{abs(left_power):02},{sign(right_power)},{abs(right_power):02}]')
                        self.log.append((left_power,right_power))
                        display(frame,obj,self.state,obj_color,(left_power,right_power))
                        cv2.putText(frame,f"supporting approaching"  ,(200, 120),cv2.FONT_HERSHEY_SIMPLEX,0.5,obj_color,2,)
                    elif self.catching == 'o' and gate_blue_missing:
                        # turn left if the car try to trace the blue gate
                        if orange_gate.area < 15000:
                            #try to use the orange gate to locate the blue gate
                            left_power,right_power = self.supporting_aim_process.run(area=orange_gate.area,cx=orange_gate.cx,parameters=supporting_aim_process_run_parameters,offset = -50)
                        else:
                            #turn left
                            left_power,right_power = self.supporting_aim_process.run(area=16000,cx=0,parameters=supporting_aim_process_run_parameters,offset = -100)
                        self.send_data(f'[{sign(left_power)},{abs(left_power):02},{sign(right_power)},{abs(right_power):02}]')
                        self.log.append((left_power,right_power))
                        display(frame,obj,self.state,obj_color,(left_power,right_power))
                        cv2.putText(frame,f"supporting approaching"  ,(200, 120),cv2.FONT_HERSHEY_SIMPLEX,0.5,obj_color,2,)

                for obj in obj_lst:

                    obj_color = define_obj_color(obj)
                    if obj.n == "ball_red":
                        if self.state == "c":
                            # if the car is in catching state
                            self.catching = 'r'
                            # catching red ball
                            if True == self.catch_process.state_change(sx=obj.s[0],cx=obj.cx,parameters=catch_process_decision_parameters):
                                # change state to 'a' if the ball is in the catching area
                                self.state = 'a'
                                
                            left_power,right_power = self.catch_process.run(area=obj.area,cx=obj.cx,parameters=catch_process_run_parameters)
                            # move the car to catch the ball, based on the position of the ball
                            self.log.append((left_power,right_power))
                            self.send_data(f'[{sign(left_power)},{abs(left_power):02},{sign(right_power)},{abs(right_power):02}]')
                            # display the information on the frame
                            display(frame,obj,self.state,obj_color,(left_power,right_power))
                            break

                    elif obj.n == "ball_green":
                        if self.state == "c":
                            # if the car is in catching state
                            self.catching = 'g'
                            # catching green ball
                            if True == self.catch_process.state_change(sx=obj.s[0],cx=obj.cx,parameters=catch_process_decision_parameters):
                                # change state to 'a' if the ball is in the catching area
                                self.state = 'a'
                            left_power,right_power = self.catch_process.run(area=obj.area,cx=obj.cx,parameters=catch_process_run_parameters)
                            # move the car to catch the ball, based on the position of the ball
                            self.log.append((left_power,right_power))
                            self.send_data(f'[{sign(left_power)},{abs(left_power):02},{sign(right_power)},{abs(right_power):02}]')
                            # display the information on the frame
                            display(frame,obj,self.state,obj_color,(left_power,right_power))
                            break
                            
                    elif obj.n == "ball_blue":
                        if self.state == "c":
                            # if the car is in catching state
                            self.catching = 'b'
                            # catching blue ball
                            if True == self.catch_process.state_change(sx=obj.s[0],cx=obj.cx,parameters=catch_process_decision_parameters):
                                # change state to 'a' if the ball is in the catching area
                                self.state = 'a'
                            left_power,right_power = self.catch_process.run(area=obj.area,cx=obj.cx,parameters=catch_process_run_parameters)
                            # move the car to catch the ball, based on the position of the ball
                            self.log.append((left_power,right_power))
                            self.send_data(f'[{sign(left_power)},{abs(left_power):02},{sign(right_power)},{abs(right_power):02}]')
                            # display the information on the frame
                            display(frame,obj,self.state,obj_color,(left_power,right_power))
                            break

                    elif obj.n == "ball_orange":
                        if self.state == "c":
                            # if the car is in catching state
                            self.catching = 'o'
                            # catching orange ball
                            if True == self.catch_process.state_change(sx=obj.s[0],cx=obj.cx,parameters=catch_process_decision_parameters):
                                # change state to 'a' if the ball is in the catching area
                                self.state = 'a'     
                            left_power,right_power = self.catch_process.run(area=obj.area,cx=obj.cx,parameters=catch_process_run_parameters)
                            # move the car to catch the ball, based on the position of the ball
                            self.log.append((left_power,right_power))
                            self.send_data(f'[{sign(left_power)},{abs(left_power):02},{sign(right_power)},{abs(right_power):02}]')
                            # display the information on the frame
                            display(frame,obj,self.state,obj_color,(left_power,right_power))
                            break
                        
                    elif obj.n == "gate_blue":
                        if self.state == "a" and self.catching == 'o':
                            # if the car is in aim state and the car is catching the orange ball
                            if True == self.aim_process.state_change(area=obj.area,cx=obj.cx,parameters=blue_gate_aim_process_decision_parameters):
                                # change state to 's' if the gate is in the shooting area
                                self.state = 's'
                            
                            left_power,right_power = self.aim_process.run(area=obj.area,cx=obj.cx,parameters=aim_process_run_parameters,offset = 0)
                            # move the car to aim at the blue gate, based on the position of the gate
                            self.send_data(f'[{sign(left_power)},{abs(left_power):02},{sign(right_power)},{abs(right_power):02}]')
                            self.log.append((left_power,right_power))
                            # display the information on the frame
                            display(frame,obj,self.state,obj_color,(left_power,right_power))
                            break

                        elif self.state == 's':
                            # if the car is in shooting state
                            # shoot the ball to the blue gate
                            left_power,right_power = (80,70)
                            self.log.append((left_power,right_power))
                            self.send_data(f"[+,{left_power},+,{right_power}]")

                            display(frame,obj,'shoot',obj_color,(left_power,right_power))

                            if True == self.state_change(area=obj.area,cx=obj.cx,parameters=blue_gate_shoot_process_decision_parameters):
                                # change state to 'stop' if the gate is in the stop area
                                self.state ='stop'
                            break
                        elif self.state == 'stop':
                            #  if the car is in stop state
                            # stop the car
                            left_power,right_power = (0,0)
                            self.log.append((left_power,right_power))
                            self.send_data("[+,00,+,00]")                
                            display(frame,obj,'stop',obj_color,(left_power,right_power))
                            break

                    elif obj.n == "gate_white":
                        if self.state == "a" and (self.catching == 'g' or self.catching == 'r' or self.catching == 'b'):
                            # if the car is in aim state and the car is catching the green or red or blue ball
                            # aim at the white gate
                            print(obj.n,obj.area,obj.cx,self.aim_process.state_change(area=obj.area,cx=obj.cx,parameters=aim_process_decision_parameters))
                            if True == self.aim_process.state_change(area=obj.area,cx=obj.cx,parameters=aim_process_decision_parameters):
                                self.state = 's'
                            # move the car to aim at the white gate, based on the position of the gate
                            left_power,right_power = self.aim_process.run(area=obj.area,cx=obj.cx,parameters=white_gate_aim_process_run_parameters,offset = 120)
                            self.send_data(f'[{sign(left_power)},{abs(left_power):02},{sign(right_power)},{abs(right_power):02}]')
                            self.log.append((left_power,right_power))
                            display(frame,obj,self.state,obj_color,(left_power,right_power))
                            break
                        elif self.state == 's':
                            # if the car is in shooting state
                            # shoot the ball to the white gate
                            left_power,right_power = (73,67)
                            self.send_data(f"[+,{left_power},+,{right_power}]")
                            self.log.append((left_power,right_power))
                            display(frame,obj,'shoot',obj_color,(left_power,right_power))
                            
                            if True == self.state_change(area=obj.area,cx=obj.cx,parameters=shoot_process_decision_parameters):
                                # change state to 'stop' if the gate is in the stop area
                                self.state = 'stop'
                            break
                        elif self.state == 'stop':
                            # if the car is in stop state
                            # stop the car
                            left_power,right_power = (0,0)
                            self.log.append((left_power,right_power))
                            self.send_data("[+,00,+,00]")                
                            display(frame,obj,'stop',obj_color,(left_power,right_power))
                            break
                
            else:
                # If no objects are detected, stop the car
                self.send_data("[+,00,+,00]")
            # Display the frame with detections
            cv2.imshow('YOLOv5 Webcam', frame)
            
            num = 0
            for log_item in log_list:
                # fill the log with None if the length of the log is less than tick
                # which means the object is not detected in this tick
                if len(log_item) < tick:
                    print(num)
                    print('tick',tick)
                    #print(log_item)
                    log_item.append((None,None,None,None,None))
                    num+=1
            if len(self.log) < tick:
                    #print(log_item)
                    self.log.append((None,None))

            key = cv2.waitKey(1) & 0xFF
            # Check for key presses
            if key == ord('r'):
                # Reset the state and stop the car
                df = pd.DataFrame({
                        "gate_white" : self.gate_white,
                        "gate_blue" : self.gate_blue,
                        "ball_red" : self.ball_red,
                        "ball_green" : self.ball_green,
                        "ball_orange" : self.ball_orange,
                        "ball_blue" : self.ball_blue,
                        "log" : self.log
                    })
                
                self.cnt += 1
                self.send_data("[+,00,+,00]")
                self.state = 'init'
                
                t = time.localtime()
                current_time = time.strftime("%H_%M_%S", t)
                # Save the log to a CSV file
                df.to_csv(f'{current_time}{self.cnt}.csv', index=False)
                #new_visualizer = visualizer(f'{current_time}{self.cnt}.csv')
                #new_visualizer.visualize()
                # reset the state and stop the car
                tick = 0 
                self.gate_white = []
                self.gate_blue = []
                self.ball_red =[]
                self.ball_green = []
                self.ball_orange = []
                self.ball_blue = []
                self.log = []
                self.cnt = 0
                print("Reset")

            elif key == ord('s'):
                    # Start the car and set the state to 'c'
                    self.send_data("[+,00,+,00]")
                    self.state = 'c'
                    print("Start")

            # Break on 'q' key press
            elif key == ord('q'):
                self.send_data("[+,00,+,00]")
                print("Exiting webcam...")
                break

            

            
                
        # Release the webcam and close OpenCV windows
        self.cap.release()
        cv2.destroyAllWindows()

    # Function to detect objects in the frame
    # This function processes the detected objects, draws bounding boxes, and updates the object list.
    def detect_obj(self,detections,frame,tick):
        obj_lst = []

        for _, row in detections.iterrows():
                    # Extract bounding box coordinates and other info
                    x1, y1, x2, y2, conf, cls, name = (
                        int(row["xmin"]),            
                        int(row["ymin"]),
                        int(row["xmax"]),
                        int(row["ymax"]),
                        row["confidence"],
                        int(row["class"]),
                        row["name"],
                    )
                    # Check if the confidence is above a certain threshold
                    if(0.5<conf):
                        obj_color = (255,0,0)                         
                        # Draw bounding box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color=(255,0,0), thickness=2)
                        
                        # Draw Center box
                        m_Object_Center_X_line = int(((x2-x1)/2)+x1)
                        m_Object_Center_Y = int(((y2-y1)/2)+y1)
                        cv2.rectangle(frame, (m_Object_Center_X_line-5, m_Object_Center_Y-5), (m_Object_Center_X_line+5, m_Object_Center_Y+5), color=(255,0,0), thickness=2)

                        # Object Size
                        m_Object_Size_X = x2-x1
                        m_Object_Size_Y = y2-y1
                        cv2.line(frame, (x1, y2) , (x2, y2), color=(255, 0, 0), thickness=4)

                        # obj build 
                        new_obj = detected_object.obj(name,(m_Object_Size_X,m_Object_Size_Y),m_Object_Center_X_line,m_Object_Center_Y)
                        obj_lst.append(new_obj)
                        # Put label and confidence score
                        label = f"{name} {conf:.2f} {new_obj.s[0]} {new_obj.area} {new_obj.cx}"
                        cv2.putText(
                            frame,
                            label,
                            (x1, y1 + 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            obj_color,
                            2
                        )
                        
                        # save the object to the log
                        if name == "gate_white":
                            self.gate_white.append((new_obj.s[0],new_obj.area,new_obj.cx,new_obj.x,new_obj.y))
                        elif name == "gate_blue":
                            self.gate_blue.append((new_obj.s[0],new_obj.area,new_obj.cx,new_obj.x,new_obj.y))
                        elif name == "ball_red":
                            self.ball_red.append((new_obj.s[0],new_obj.area,new_obj.cx,new_obj.x,new_obj.y))
                        elif name == "ball_blue":
                            self.ball_blue.append((new_obj.s[0],new_obj.area,new_obj.cx,new_obj.x,new_obj.y))
                        elif name == "ball_green":
                            self.ball_green.append((new_obj.s[0],new_obj.area,new_obj.cx,new_obj.x,new_obj.y))
                        elif name == "ball_orange":
                            self.ball_orange.append((new_obj.s[0],new_obj.area,new_obj.cx,new_obj.x,new_obj.y))
                        
                        num = 0
                        log_list = [self.gate_white,self.gate_blue,self.ball_red,self.ball_blue,self.ball_green,self.ball_orange,self.log]
                        for log_item in log_list:
                            # if there is more than one same object in the log, pop the last element and append it to the current object
                            if len(log_item) > tick:
                                print('tick',tick)
                                print(num)
                                last_element = log_item.pop()
                                last_sec_element = log_item.pop()
                                if isinstance(last_sec_element,list):
                                    last_sec_element.append(last_element)
                                    log_item.append(last_sec_element)
                                else:
                                    log_item.append([last_sec_element,last_element])
                                #print(log_item)
                            num+=1

                            
        return obj_lst,frame
        
if __name__ == "__main__":
    model_path = '/home/wheeltec/PycharmProjects/PythonProject/Yolo/14AprV1_b/13042.pt'
    main_process = main_process(model_path)
    main_process.send_data("[+,00,+,00]")
    main_process.run()


