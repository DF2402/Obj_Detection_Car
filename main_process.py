import catch_process
import aim_process
import math 
import pandas as pd
import detected_object

import cv2
import torch
import numpy as np
import math
import time
import serial
import random

decision_area = 400*400
decision_dcx = 300
catch_process_decision_parameters = (decision_area,decision_dcx)

decision_area = 550*550
decision_dcx = 250
aim_process_decision_parameters =  (decision_area,decision_dcx)

decision_area = 800*800
decision_dcx = 400
shoot_process_decision_parameters =  (decision_area,decision_dcx)


diff_speed_limit = 50
left_ratio = 0.5
right_ratio = 0.5
base_speed = 10
base_speed_limit = 50
slow_ratio = 2
catch_process_run_parameters = (diff_speed_limit,left_ratio,right_ratio, base_speed,base_speed_limit,slow_ratio)

diff_speed_limit = 50
left_ratio = 0.5
right_ratio = 0.5
base_speed = 10
base_speed_limit = 50
slow_ratio = 2
aim_process_run_parameters = (diff_speed_limit,left_ratio,right_ratio, base_speed,base_speed_limit,slow_ratio)

model_path = 'C:/project_local/EIE3360_Project/23Mar/best.pt'

class main_process():
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
        self.aim_process = aim_process.aim_process()
        self.state = 'init'
        self.catching = None
    # Function to send data over UART
    def send_data(self,data):
        if self.ser.isOpen():
            self.ser.write(data.encode())  # Convert string to bytes and send
            print(f"UART Command : {data}")
        else:
            print("UART port is not open!")

    def state_change(self,area,cx,parameters=(360000,250)):
        decision_area, decision_dcx = parameters
        cx = abs(cx)
        if (decision_area <= area and decision_dcx >= cx ):
            return True
        return False
    
    def run(self):
        def sign(int_input):
            return '-' if int_input < 0 else '+'
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Could not read frame from webcam.")
                break
            center_x_line = int(1280/2)
            center_y_line = int(720/2)
            left_line = int(center_x_line-200)
            bot_line = int(center_y_line-200)
            right_line = int(center_x_line+200)
            up_line = int(center_y_line+200)
            
            # draw lines
            color = (255, 0, 0)               # Line color (BGR): Blue
            thickness = 1                     # Line thickness
            cv2.line(frame, (left_line, 0) , (left_line, 720) , color, thickness)
            cv2.line(frame, (right_line, 0) , (right_line, 720), color, thickness)
            cv2.line(frame, (0, bot_line) , (1280, bot_line) , color, thickness)
            cv2.line(frame, (0, up_line) , (1280, up_line), color, thickness)

            # Convert the frame to RGB (YOLOv5 expects RGB input)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Perform inference
            results = self.model(frame_rgb)

            # Parse detection results and plot them directly on the frame
            detections = results.pandas().xyxy[0]  # Get the detections as a Pandas DataFrame
            m_Number_Object_01 = len(detections)
            obj_lst = []

            if(0<m_Number_Object_01):
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

                    if(0.5<conf):
                        if name == 'ball_red':
                            obj_color = (255,0,0)
                        elif name == 'ball_green':
                            obj_color= (0,255,0)
                        elif name == 'gate_orange':
                            obj_color= (235, 119, 52)
                        elif name == 'gate_white':
                            obj_color= (255,255,255)
                        else:
                            obj_color= (0,0,255)

                        # Draw bounding box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color=obj_color, thickness=2)
                        
                        # Draw Center box
                        m_Object_Center_X_line = int(((x2-x1)/2)+x1)
                        m_Object_Center_Y = int(((y2-y1)/2)+y1)
                        cv2.rectangle(frame, (m_Object_Center_X_line-5, m_Object_Center_Y-5), (m_Object_Center_X_line+5, m_Object_Center_Y+5), color=obj_color, thickness=2)

                        # Object Size
                        m_Object_Size_X = x2-x1
                        m_Object_Size_Y = y2-y1
                        cv2.line(frame, (x1, y2) , (x2, y2), color=(255, 0, 0), thickness=4)

                        # obj build 
                        new_obj = detected_object.obj(name,(m_Object_Size_X,m_Object_Size_Y),m_Object_Center_X_line,m_Object_Center_Y)
                        obj_lst.append(new_obj)
                        # Put label and confidence score
                        label = f"{name} {conf:.2f} {m_Object_Size_X}"

                        cv2.putText(
                            frame,
                            label,
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            obj_color,
                            2,
                        )
                for obj in obj_lst:
                    
                    if obj.n == "ball_red":
                        if self.state == "c":
                            self.catching = 'r'
                            if True == self.catch_process.state_change(area=obj.area,cx=obj.cx,decision_parameters=catch_process_decision_parameters):
                                self.state = 'a'
                                break 
                
                            left_power,right_power = self.catch_process.run(area=obj.area,cx=obj.cx,parameters=catch_process_run_parameters)
                            self.send_data(f'[{sign(left_power)},{abs(left_power):02},{sign(right_power)},{abs(right_power):02}]')

                            cv2.putText(frame,f"red ball:{obj.area} {obj.cx}"  ,(200, 40),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0),2,)
                            cv2.putText(frame,"approching red ball"  ,(200, 60),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0),2,)
                            cv2.putText(frame,f"power: {left_power,right_power}"  ,(200, 80),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0),2,)

                    elif obj.n == "ball_green":
                        
                        if self.state == "c":
                            self.catching = 'g'
                            if True == self.catch_process.state_change(area=obj.area,cx=obj.cx,decision_parameters=catch_process_decision_parameters):
                                self.state = 'a'
                                break  

                            left_power,right_power = self.catch_process.run(area=obj.area,cx=obj.cx,parameters=catch_process_run_parameters)
                            self.send_data(f'[{sign(left_power)},{abs(left_power):02},{sign(right_power)},{abs(right_power):02}]')

                            cv2.putText(frame,f"green ball:{obj.area} {obj.cx}"  ,(200, 40),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0),2,)
                            cv2.putText(frame,"approching green ball"  ,(200, 60),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0),2,)
                            cv2.putText(frame,f"power: {left_power,right_power}"  ,(200, 80),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0),2,)
                            
                    
                    elif obj.n == "gate_orange":
                        if self.state == "a" and self.catching == 'r':
                            if True == self.aim_process.state_change(area=obj.area,cx=obj.cx,decision_parameters=aim_process_decision_parameters):
                                self.state = 's'
                                break  

                            left_power,right_power = self.aim_process.run(area=obj.area,cx=obj.cx,parameters=aim_process_run_parameters)
                            self.send_data(f'[{sign(left_power)},{abs(left_power):02},{sign(right_power)},{abs(right_power):02}]')

                            cv2.putText(frame,f"orange gate:{obj.area} {obj.cx}"  ,(200, 40),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0),2,)
                            cv2.putText(frame,"approching orange gate"  ,(200, 60),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0),2,)
                            cv2.putText(frame,f"power: {left_power,right_power}"  ,(200, 80),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0),2,) 

                        elif self.state == 's':
                            left_power,right_power = (99,99)
                            self.send_data(f"[+,{left_power},+,{right_power}]")

                            cv2.putText(frame,f"orange gate:{obj.area} {obj.cx}"  ,(200, 40),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0),2,)
                            cv2.putText(frame,"Shoot"  ,(200, 60),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0),2,)
                            cv2.putText(frame,f"power: {left_power,right_power}"  ,(200, 80),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0),2,) 

                            if True == self.state_change(area=obj.area,cx=obj.cx,decision_parameters=shoot_process_decision_parameters):
                                left_power,right_power = (0,0)
                                self.send_data("[+,00,+,00]")

                                cv2.putText(frame,f"orange gate:{obj.area} {obj.cx}"  ,(200, 40),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0),2,)
                                cv2.putText(frame,"stop"  ,(200, 60),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0),2,)
                                cv2.putText(frame,f"power: {left_power,right_power}"  ,(200, 80),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0),2,) 
                                 

                    elif obj.n == "gate_white":
                        if self.state == "a" and self.catching == 'g':
                            if True == self.aim_process.state_change(area=obj.area,cx=obj.cx,decision_parameters=aim_process_decision_parameters):
                                self.state = 's'
                                break  

                            left_power,right_power = self.aim_process.run(area=obj.area,cx=obj.cx,parameters=aim_process_run_parameters)
                            self.send_data(f'[{sign(left_power)},{abs(left_power):02},{sign(right_power)},{abs(right_power):02}]')

                            cv2.putText(frame,f"white gate:{obj.area} {obj.cx}"  ,(200, 40),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0),2,)
                            cv2.putText(frame,"approching white gate"  ,(200, 60),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0),2,)
                            cv2.putText(frame,f"power: {left_power,right_power}"  ,(200, 80),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0),2,)  

                        elif self.state == 's':
                            left_power,right_power = (99,99)
                            self.send_data(f"[+,{left_power},+,{right_power}]")

                            cv2.putText(frame,f"white gate:{obj.area} {obj.cx}"  ,(200, 40),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0),2,)
                            cv2.putText(frame,"Shoot"  ,(200, 60),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0),2,)
                            cv2.putText(frame,f"power: {left_power,right_power}"  ,(200, 80),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0),2,) 
                            
                            if True == self.state_change(area=obj.area,cx=obj.cx,decision_parameters=shoot_process_decision_parameters):
                                left_power,right_power = (0,0)
                                self.send_data("[+,00,+,00]")

                                cv2.putText(frame,f"white gate:{obj.area} {obj.cx}"  ,(200, 40),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0),2,)
                                cv2.putText(frame,"stop"  ,(200, 60),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0),2,)
                                cv2.putText(frame,f"power: {left_power,right_power}"  ,(200, 80),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0),2,) 
            else:
                self.send_data("[+,00,+,00]")
            # Display the frame with detections
            cv2.imshow('YOLOv5 Webcam', frame)

            # Break on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.send_data("[+,00,+,00]")
                print("Exiting webcam...")
                break
            elif cv2.waitKey(1) & 0xFF == ord('r'):
                self.send_data("[+,00,+,00]")
                self.state = 'c'
                print("Reload")
                
                

        # Release the webcam and close OpenCV windows
        self.cap.release()
        cv2.destroyAllWindows()
        
if __name__ == "__main__":
    main_process = main_process(model_path)
    main_process.run()


