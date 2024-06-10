// File:          inspection_controller.cpp
// Date:          1-11-23
// Description:   RugRobot simulation controller for tiled setup
// Author:        Thiemen Siemensma
// Modifications:

#include <stdlib.h>
#include <cstdlib>
#include <math.h>
#include <iostream>
#include <fstream>
#include <string>
#include <sstream> 
#include <time.h>
#include <webots/Robot.hpp> 
#include <webots/Motor.hpp>
#include <webots/Gyro.hpp>
#include <webots/Accelerometer.hpp>
#include <webots/Camera.hpp>
#include <webots/DistanceSensor.hpp>
#include <webots/Emitter.hpp>
#include <webots/Receiver.hpp>
#include <webots/Keyboard.hpp>
#include <webots/PositionSensor.hpp>
#include <webots/Supervisor.hpp>
#include <queue>
#include <vector>
#include <cmath>
#include <unistd.h>
#include "environment.hh"
#include "RugBot_Algorithms.hh"

// All the webots classes are defined in the "webots" namespace
using namespace webots;

// Initialize the parameters

#define STOP 1.0e-8
#define TINY 1.0e-30

enum Side { LEFT, RIGHT, FORWARD, BACKWARD };

int main(int argc, char **argv) {
  std::cout << "Starting main " << '\n';
  Environment arena = Environment("world.txt",false);
  RugRobot robot;
  robot.setSpeed(100,100);
  //robot.run(); 
}

