#ifndef INCLUDED_ROVABLE_H_
#define INCLUDED_ROVABLE_H_

#include <algorithm>
#include <webots/DistanceSensor.hpp>
#include <webots/Emitter.hpp>
#include <webots/Robot.hpp>
#include <webots/Supervisor.hpp>
#include <webots/Emitter.hpp>
#include <webots/Receiver.hpp>
#include <webots/Motor.hpp>
#include <webots/Gyro.hpp>
#include <random>
#include <cmath>

using namespace webots;

class RugRobot {
private:
    Supervisor *d_robot;
    Motor *leftMotor;
    Motor *rightMotor;
    Gyro *gyro;
    Node *d_this_robot_node;
    Field *translationData;
    Field *customData;
    Emitter *emitter;
    Receiver *receiver;

    std::size_t static const n_sensors = 3;
    const char *distance_sensors_names[n_sensors] = {
        "left distance sensor", 
        "right distance sensor", 
        "middle distance sensor"
    };
    DistanceSensor *d_distance_sensors[n_sensors];
    const char *dMotorNames[2] = {"left motor", "right motor"};

    double lower_bound_angle = -0.125;
    double upper_bound_angle = 0.125;
    double lower_bound_speed = 0.95;
    double upper_bound_speed = 1.05;
    double speed_dev = 1;
    double motor_dev = 0;

    double refAngle = 0;
    double angleIntegrator = 0;

    enum RStates {
        STATE_FW,                       
        STATE_BW,                       
        STATE_TR,                      
        STATE_RL,                    
        STATE_PAUSE,
        STATE_RESET,
        STATE_RECV,
        STATE_SEND,
    };
public:
    RStates state = STATE_PAUSE;

    RugRobot();
    ~RugRobot();
    void setSpeed(double speedl, double speedr);
    void turnAngle(double Angle);
    void clearAngle();
    void sendMessage(const int *data, int size);
    std::vector<int> RugRobot::getMessages();

    enum {TIME_STEP = 20};
};

RugRobot::RugRobot() {
    d_robot = new Supervisor();

    for (std::size_t i = 0; i < n_sensors; ++i) {
        d_distance_sensors[i] = d_robot->getDistanceSensor(distance_sensors_names[i]);
        d_distance_sensors[i]->enable(TIME_STEP);
    }

    leftMotor = d_robot->getMotor(dMotorNames[0]);
    rightMotor = d_robot->getMotor(dMotorNames[1]);
    leftMotor->setPosition(INFINITY);
    rightMotor->setPosition(INFINITY);
    leftMotor->getMaxTorque();
    leftMotor->setVelocity(0);
    rightMotor->setVelocity(0);

    d_this_robot_node = d_robot->getSelf();
    translationData = d_this_robot_node->getField("translation");
    customData = d_this_robot_node->getField("customData");

    gyro = d_robot->getGyro("gyro");
    gyro->enable(TIME_STEP); 

    std::string name = d_robot->getName();
    int SeedRov = ((int) name[1]) * 10;
    srand(SeedRov);
    std::cout << "RugRobot " << name[1] << " with Seed " << SeedRov << '\n';
    std::default_random_engine generator(SeedRov);
    std::uniform_real_distribution<double> angle_dist(lower_bound_angle, upper_bound_angle);
    std::uniform_real_distribution<double> speed_dist(lower_bound_speed, upper_bound_speed);

    motor_dev = angle_dist(generator);
    speed_dev = speed_dist(generator);
    std::cout << "Motor deviations[a,s]:" << motor_dev << ',' << speed_dev << '\n';
}

RugRobot::~RugRobot() {
    delete d_robot;
}

void RugRobot::setSpeed(double speedl, double speedr) {
    speedl = std::clamp(speedl, -100.0, 100.0);
    speedr = std::clamp(speedr, -100.0, 100.0);

    leftMotor->setVelocity(speedl / 100 * (1 - motor_dev) * speed_dev * 10);
    rightMotor->setVelocity(speedr / 100 * (1 + motor_dev) * speed_dev * 10);
}

void RugRobot::turnAngle(double Angle) {
    double Pgain = 2.5;
    double Igain = 0.1;
    double dt = TIME_STEP / 1000.0;
    double e = Angle - refAngle;

    double gyro_val_z = gyro->getValues()[2] * 180 / M_PI;
    angleIntegrator += e * dt;
    refAngle += gyro_val_z * dt;

    if (std::abs(e) > 2.5) {
        double left = -Pgain * e - Igain * angleIntegrator;
        double right = Pgain * e + Igain * angleIntegrator;
        setSpeed(left, right);
    } else {
        clearAngle();
        setSpeed(0, 0);
        // Handle state transition if necessary
    }
}

void RugRobot::clearAngle() {
    refAngle = 0;
    angleIntegrator = 0;
}

void RugRobot::sendMessage(const int *data, int size) {
    emitter->send(data, size * sizeof(int));
}

std::vector<int> RugRobot::getMessages() {
    std::vector<int> messages;

    while (receiver->getQueueLength() > 0) {
        const int *data = (const int*)receiver->getData();
        int dataSize = receiver->getDataSize() / sizeof(int);

        for (int i = 0; i < dataSize; ++i) {
            messages.push_back(data[i]);
        }

        receiver->nextPacket();
    }

    return messages;
}



#endif
