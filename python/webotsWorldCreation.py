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
    def __init__(self, run, instance, seed, name, n_robots) -> None:
        self.run = run
        self.instance = instance
        self.seed = seed
        self.name = name
        self.n_robots = n_robots
        self.run_dir = f"jobfiles/Run_{self.run}/"

    def create_header(self):
        self.file.write("""#VRML_SIM R2023b utf8
EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023b/projects/objects/backgrounds/protos/TexturedBackground.proto"
EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023b/projects/objects/backgrounds/protos/TexturedBackgroundLight.proto"
EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023b/projects/objects/apartment_structure/protos/Wall.proto"
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
  appearance Appearance {
    material Material {
      diffuseColor 0.8 0.8 0.8
    }
  }
}
Wall {
  translation 0.5 0 1
  name "wall(1)"
  size 1 0.05 0.025
  appearance Appearance {
    material Material {
      diffuseColor 0.8 0.8 0.8
    }
  }
}
Wall {
  translation 1 0 0.5
  rotation 0 1 0 1.5708
  name "wall(2)"
  size 1 0.05 0.025
  appearance Appearance {
    material Material {
      diffuseColor 0.8 0.8 0.8
    }
  }
}
Wall {
  translation -0.025 0 0.5
  rotation 0 1 0 1.5708
  name "wall(3)"
  size 1 0.05 0.025
  appearance Appearance {
    material Material {
      diffuseColor 0.8 0.8 0.8
    }
  }
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
        
        positions = set()
        min_distance = 0.04
        max_attempts = 1000
        
        for i in range(self.n_robots):
          attempts = 0
          while attempts < max_attempts:
              x = random.uniform(0.05,0.95)
              y = random.uniform(0.05,0.95)
              POSE = rotate_Y(random.uniform(0,math.pi*2))
              
              if all(math.sqrt((x - px) ** 2 + (y - py) ** 2) >= min_distance for px, py in positions):
                  positions.add((x, y))
                  self.initialX.append(x)
                  self.initialY.append(y)
                  self.rx.append(POSE[0])
                  self.ry.append(POSE[1])
                  self.rz.append(POSE[2])
                  self.w.append(POSE[3])
                  if i == 0:
                      print(self.initialX, self.initialY, self.rx, self.ry, self.rz, self.w)
                  break
              attempts += 1
              
        if len(positions) < self.n_robots:
            print(f"Could not find positions for {self.n_robots - len(positions)} robots. Adding the rest at random positions.")
            for i in range(self.n_robots - len(positions)):
                x = random.uniform(0.05,0.95)
                y = random.uniform(0.05,0.95)
                POSE = rotate_Y(random.uniform(0,math.pi*2))
                self.initialX.append(x)
                self.initialY.append(y)
                self.rx.append(POSE[0])
                self.ry.append(POSE[1])
                self.rz.append(POSE[2])
                self.w.append(POSE[3])
                positions.add((x, y))
        


    def save_settings(self,c_settings,s_settings):
        # Open a file in write mode

        fcsettings =  f"{self.run_dir}Instance_{self.instance}/c_settings.txt"
        fssettings =  f"{self.run_dir}Instance_{self.instance}/s_settings.txt"
        for file,setting in zip([fcsettings,fssettings],[c_settings,s_settings]):
            with open(file, 'w') as file:
                for value in setting.values():
                    file.write(str(value) + '\n')



    def create_world(self):
        np.random.seed(self.seed)
        random.seed(self.seed)
        self.file = open(r"worlds/" + self.name+ ".wbt", 'w')
        self.randomizePosition()
        self.create_header()
        self.create_robots_in_world()
        self.file.close()
