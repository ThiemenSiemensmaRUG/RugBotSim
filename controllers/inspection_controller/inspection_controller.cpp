// File:          inspection_controller.cpp
// Date:          1-11-23
// Description:   RugBot simulation controller
// Author:        Thiemen Siemensma
// Modifications:

#include <math.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <queue>
#include <sstream>
#include <string>
#include <vector>
#include <webots/Accelerometer.hpp>
#include <webots/Camera.hpp>
#include <webots/DistanceSensor.hpp>
#include <webots/Emitter.hpp>
#include <webots/Gyro.hpp>
#include <webots/Keyboard.hpp>
#include <webots/Motor.hpp>
#include <webots/PositionSensor.hpp>
#include <webots/Receiver.hpp>
#include <webots/Robot.hpp>
#include <webots/Supervisor.hpp>

#include "StateMachine.hh"

// All the webots classes are defined in the "webots" namespace
using namespace webots;

// Initialize the parameters

#define STOP 1.0e-8
#define TINY 1.0e-30

enum Side {LEFT, RIGHT, FORWARD, BACKWARD};

int main(int argc, char **argv) {
    StateMachine stateMachine;
    stateMachine.run();
}
