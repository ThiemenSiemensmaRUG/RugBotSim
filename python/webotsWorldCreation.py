import math
import numpy as np  
import random  
from PIL import Image, ImageDraw 
from scipy.spatial.transform import Rotation as R
import argparse




def rotate_Y(angle_rad):
    Init = R.from_matrix(np.array([[1, 0 , 0],
                                        [0,np.cos(-np.pi/2) , -np.sin(-np.pi/2)],
                                        [0,np.sin(-np.pi/2) , np.cos(-np.pi/2)]]))
    RotationY = R.from_matrix(np.array([[np.cos(angle_rad), 0 , np.sin(angle_rad)],
                                        [0, 1 , 0],
                                        [-np.sin(angle_rad), 0 , np.cos(angle_rad)]]))
    Rotation = RotationY *Init    
    Rotation = Rotation.as_quat()
    angle = np.arccos(Rotation[3])*2
    axis = Rotation[0:3] / np.sin(angle/2)
    total = np.array(axis)
    total = np.append(total,angle)
    return list(total)



class createWorld():
    def __init__(self,instance,seed,name,n_robots) -> None:
        self.instance = instance
        self.seed = seed
        self.name = name
        self.n_robots = n_robots


    def create_header(self):
        self.file.write("""#VRML_SIM R2023b utf8

EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023b/projects/objects/backgrounds/protos/TexturedBackground.proto"
EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023b/projects/objects/backgrounds/protos/TexturedBackgroundLight.proto"
EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023b/projects/appearances/protos/Plastic.proto"
EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023b/projects/appearances/protos/CorrodedMetal.proto"
EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023b/projects/appearances/protos/BrushedAluminium.proto"                                                                   
EXTERNPROTO "../protos/RovableV2.proto"
                        

WorldInfo {
  CFM 0.1
  ERP 0.1
  basicTimeStep 20
  coordinateSystem "NUE"
  contactProperties [
    ContactProperties {
      material2 "WheelMat"
    }
  ]
}
Viewpoint {
  orientation 0.1925921807186387 -0.6691465356635923 -0.7177403191513292 2.316919496005195
  position 2.2084568665922713 2.0198270618414162 -0.09752769031243588
}
TexturedBackground {
}
TexturedBackgroundLight {
}
DEF surface Solid {
  translation 0.5 0 0.5
  rotation -0.9999999999999999 0 0 1.5707953071795862
  children [
    Shape {
      appearance Appearance {
        texture ImageTexture {
          url [
            ""
          ]
        }
      }
      geometry Plane {
      }
    }
  ]
  contactMaterial "Metal"
  boundingObject Plane {
  }
}
Wall {
  translation 0.5 0 -0.025
  size 1 0.05 0.025
}
Wall {
  translation 0.5 0 1
  name "wall(1)"
  size 1 0.05 0.025
}
Wall {
  translation 1 0 0.5
  rotation 0 1 0 1.5708
  name "wall(2)"
  size 1 0.05 0.025
}
Wall {
  translation -0.025 0 0.5
  rotation 0 1 0 1.5708
  name "wall(3)"
  size 1 0.05 0.025
}
Robot {
  name "Bayes Bot Supervisor"
  controller "cpp_supervisor"
  controllerArgs [
    "0"
  ]
  supervisor TRUE
}\n   """)
        
    def create_robots_in_world(self):
        arg = "\"" + str(self.instance) + "\""
        for i in range(int(self.n_robots)):
            rov_number = str(i)
            rotationArg = str(self.rx[i]) + " " + str(self.ry[i]) + " " + str(self.rz[i]) + " " + str(self.w[i]) 
            self.file.write(
                """DEF r""" + rov_number + """ RovableV2 {
    translation """ + str(self.initialX[i]) + """ 0.0125 """ + str(self.initialY[i]) + """
    rotation """ + rotationArg + """
    name "r""" + rov_number + """"
    controller "inspection_controller"
    controllerArgs [
        """ + arg + """
    ]
    supervisor TRUE
    customData ""
    extensionSlot [
        Receiver {
        }
        Emitter {
        }
    ]
    }\n""")
    


    def randomizePosition(self):
        self.initialX = []
        self.initialY = []
        self.rx = []
        self.ry = []
        self.rz = []
        self.w = []
        self.orientation = [[1, 0, 0, -1.57], [0.577, 0.577, 0.577, -2.09], [0, 0.707106, 0.707107, 3.14159], [0.577, -0.577, -0.577, -2.09]]
        
        for i in range(self.n_robots):
            x = random.uniform(0.05,0.95)
            y = random.uniform(0.05,0.95)
            POSE = rotate_Y(random.uniform(0,math.pi*2))
            if ((x not in self.initialX) and (y not in self.initialY)):
                self.initialX.append(x)
                self.initialY.append(y)
                self.rx.append(POSE[0])
                self.ry.append(POSE[1])
                self.rz.append(POSE[2])
                self.w.append(POSE[3])



    def save_settings(self,run_dir,c_settings,s_settings):
        # Open a file in write mode

        fcsettings =  f"{run_dir}Instance_{self.instance}/c_settings.txt"
        fssettings =  f"{run_dir}Instance_{self.instance}/s_settings.txt"
        for file,setting in zip([fcsettings,fssettings],[c_settings,s_settings]):
            with open(file, 'w') as file:
                for value in setting.values():
                    file.write(str(value) + '\n')
            file.close()


    def saveGrid(self,run_dir=None,size=5,fill_ratio=0.48,seed = 1,grid_ = None):
        np.random.seed(seed)

        grid = np.zeros((size,size), dtype=int)
        total_cells = size*size
        filled_cells = int(fill_ratio * total_cells)

        # Get random indices to fill
        indices = np.random.choice(total_cells, filled_cells, replace=False)
        # Convert indices to row, column format
        
        row_indices, col_indices = np.unravel_index(indices, (size,size))
        # Fill the grid at selected indices
        grid[row_indices, col_indices] = 1

        if (grid_) is not None:
          grid = grid_
          print("custom grid inserted\n")

        map_list = []
        for x, row in enumerate(grid):
          for y, value in enumerate(row):
              if value == 1:
                  map_list.append((y,x))


        map = np.array(map_list)
        
        filename =f"{run_dir}Instance_{self.instance}/world.txt"

        np.savetxt(filename, map.astype(int), delimiter=',', fmt='%d', footer="-1")
        


        



    def create_world(self):
        np.random.seed(self.seed)
        random.seed(self.seed)
        self.file = open(r"worlds/" + self.name+ ".wbt",'w')
        self.randomizePosition()
        self.create_header()
        self.create_robots_in_world()
        self.file.close()


        


    
