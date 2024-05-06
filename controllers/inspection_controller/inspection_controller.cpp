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
#include "inspection_robot.hh"

// All the webots classes are defined in the "webots" namespace
using namespace webots;

// Initialize the parameters

#define STOP 1.0e-8
#define TINY 1.0e-30

enum Side { LEFT, RIGHT, FORWARD, BACKWARD };

int main(int argc, char **argv) {
  std::cout << "Starting main " << '\n';
  Environment arena = Environment("world.txt",false);
  Rover robot = Rover(arena);
  robot.run(); 
}

/*
 * zlib License
 *
 * Regularized Incomplete Beta Function
 *
 * Copyright (c) 2016, 2017 Lewis Van Winkle
 * http://CodePlea.com
 *
 * This software is provided 'as-is', without any express or implied
 * warranty. In no event will the authors be held liable for any damages
 * arising from the use of this software.
 *
 * Permission is granted to anyone to use this software for any purpose,
 * including commercial applications, and to alter it and redistribute it
 * freely, subject to the following restrictions:
 *
 * 1. The origin of this software must not be misrepresented; you must not
 *    claim that you wrote the original software. If you use this software
 *    in a product, an acknowledgement in the product documentation would be
 *    appreciated but is not required.
 * 2. Altered source versions must be plainly marked as such, and must not be
 *    misrepresented as being the original software.
 * 3. This notice may not be removed or altered from any source distribution.
 */
