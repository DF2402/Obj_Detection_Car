import pandas as pd
import numpy as np
import os
import numpy as np
import matplotlib.pyplot as plt
import cv2
import matplotlib.patches as patches
class obj:
    def __init__(self,df,name):
        self.n = name 
        self.df = df[f'{name}']
        self.x = []
        self.y = []
        self.xs = []
        self.area = []
        for row in self.df:
            item = eval(row)
            if isinstance(item, tuple): 
                self.xs.append(item[0])
                self.area.append(item[1])
                self.x.append(item[3])
                self.y.append(item[4])
            elif isinstance(item, list):  
                max_tuple = max(item, key=lambda x: x[0])
                self.xs.append(max_tuple[0])
                self.area.append(max_tuple[1])
                self.x.append(max_tuple[3])
                self.y.append(max_tuple[4])
        self.x =np.array(self.x, dtype=np.float32)
        self.y =np.array(self.y, dtype=np.float32)
        self.area = np.array(self.area,dtype=np.float32)
        self.xs = np.array(self.xs,dtype=np.float32)

class visualizer:
    # This class is used to visualize the data in a CSV file.
    # The CSV file should contain the following columns: 'log', 'ball_red', 'ball_green', 'ball_orange', 'ball_blue', 'gate_white', 'gate_blue'
    def __init__(self,path):
        self.df = pd.read_csv(path)
        self.file_name = os.path.basename(path)
    def visualize(self):
        df = self.df 
        power = df['log']
        left_power , right_power = [],[]
        for row in power:
            item = eval(row)
            left , right= item
            left_power.append(left)
            right_power.append(right)
        obj_lst = []
        obj_name = ['ball_red','ball_green','ball_orange','ball_blue','gate_white','gate_blue']
        for name in obj_name:
            new_obj = obj(df,name)
            print(name,new_obj.df.shape)
            obj_lst.append(new_obj)
        print(obj_lst)
        left_power =  np.nan_to_num(np.array(left_power, dtype=np.float32)) # 假设数据是浮点数
        right_power = np.nan_to_num(np.array(right_power, dtype=np.float32))

        # create video writer
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(f'{self.file_name}.avi', fourcc, 20.0, (1280, 720))

        # set up the plot
        plt.ion()
        fig, ax = plt.subplots(figsize=(8, 6))
        sc = ax.scatter([], [], s=100)  # 创建一个空的散点图

        # set axis limits
        ax.set_title('power')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        print(df.shape,len(df))
        # loop through each frame
        for i in range(len(df)-1):
            # clear the figure
            ax.clear()
            for objs in obj_lst:
                if objs.x[i] != None :
                    #print(objs.x[i],objs.n)
                    x = objs.x[i]
                    y = objs.y[i]
                    xs = objs.xs[i]
                    area = objs.area[i]
                    # update scatter plot
                    ax.scatter(x, y, s=100, c='blue')

                    ax.text(x + 20, y+20, f'({objs.n,area,x})', fontsize=14, verticalalignment='center')
                    
                    # calculate the width and height of the rectangle
                    width = xs  
                    height = area/width 

                    # create rectangle, centered at the point
                    rect = patches.Rectangle((x - width / 2, y- height / 2), width, height, linewidth=1, edgecolor='red', facecolor='none')
                    ax.add_patch(rect)
                
            ax.text(0.5, 0.95, f'tick:{i}/{len(df)-1} power : {left_power[i],right_power[i]}', fontsize=12, ha='center', transform=ax.transAxes)
            
            # keep the same axis limits
            ax.set_xlim(0, 1280 )
            ax.set_ylim(720, 0)
            
            # plot the figure
            plt.draw()
            plt.pause(0.01)

            # convert the figure to an image and write to video
            fig.canvas.draw()
            image = np.frombuffer(fig.canvas.tostring_argb(), dtype=np.uint8)

            height, width = fig.canvas.get_width_height()
            image = image.reshape((height, width, 4)) 
            
            out.write(cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

        # release the video writer and close the plot
        out.release()
        plt.close(fig)


if __name__ == "__main__":
    path = '/home/wheeltec/PycharmProjects/PythonProject/Yolo/12_13_081.csv'
    visualizer = visualizer(path)
    visualizer.visualize()
   
