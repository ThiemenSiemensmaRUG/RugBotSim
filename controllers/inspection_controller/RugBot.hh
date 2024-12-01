#ifndef INCLUDED_RUGBOT_HH_
#define INCLUDED_RUGBOT_HH_

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
#include <string>  

using namespace webots;



class RugRobot {
public:

    Supervisor *d_robot;
    Motor *leftMotor;
    Motor *rightMotor;
    Gyro *gyro;
    Node *d_this_robot_node;
    Field *translationData;
    Field *customData;
    Emitter *emitter;
    Receiver *receiver;

    double timeStep;
    double rw_time;
    double rw_angle;
    double ca_angle;
    double spend_time;

    double CA_Threshold = 60.0;
    std::size_t static const n_sensors = 3;
    const char *distance_sensors_names[n_sensors] = {
        "left distance sensor", 
        "right distance sensor", 
        "middle distance sensor"
    };
    DistanceSensor *d_distance_sensors[n_sensors];
    const char *dMotorNames[2] = {"left motor", "right motor"};

    double lower_bound_angle = -0.0125;
    double upper_bound_angle = 0.0125;
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
        STATE_CA,
        STATE_TURN,             
        STATE_RL,                    
        STATE_PAUSE,
        STATE_RESET,
        STATE_RECV,
        STATE_SEND,
    };

    RStates state = STATE_FW;

    std::default_random_engine generator;

    std::uniform_real_distribution<double> angle_dist;
    std::uniform_real_distribution<double> speed_dist;
    std::cauchy_distribution<double> rw_time_gen;
    std::uniform_real_distribution<double> rw_angle_gen;
    std::uniform_real_distribution<double> ca_angle_gen;



    RugRobot(double timeStep);
    ~RugRobot();
    void setSpeed(double speedl, double speedr);
    int turnAngle(double Angle);
    void clearAngle();
    void sendMessage(const int *data, int size);
    std::vector<int> getMessages();
    bool collAvoid();
    int RandomWalk();
    void generateRW();
    void setCustomData(const std::string& inputString);
    std::vector<int> getPos();

};

RugRobot::RugRobot(double timeStep) : timeStep(timeStep) {
    d_robot = new Supervisor();

    spend_time = 0;

    for (std::size_t i = 0; i < n_sensors; ++i) {
        d_distance_sensors[i] = d_robot->getDistanceSensor(distance_sensors_names[i]);
        d_distance_sensors[i]->enable(timeStep);
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
    gyro->enable(timeStep); 

    std::string name = d_robot->getName();
    int SeedRov = ((int) name[1]) * 10;
    srand(SeedRov);
    std::cout << "RugRobot " << name[1] << " with Seed " << SeedRov << '\n';
    generator.seed(SeedRov);
    angle_dist = std::uniform_real_distribution<double>(lower_bound_angle, upper_bound_angle);
    speed_dist = std::uniform_real_distribution<double>(lower_bound_speed, upper_bound_speed);
    rw_time_gen = std::cauchy_distribution<double>(7500, 1000);
    rw_angle_gen =  std::uniform_real_distribution<double>(-180.0, 180.0);
    ca_angle_gen =  std::uniform_real_distribution<double>(-180.0, 180.0);
    
    ca_angle = ca_angle_gen(generator);

    motor_dev = 0;//angle_dist(generator);
  

    speed_dev = 1;//speed_dist(generator);

    //std::cout << "Motor deviations[a,s]:" << motor_dev << ',' << speed_dev << '\n';

    generateRW();
    

    
}



RugRobot::~RugRobot() {
    delete d_robot;
}


void RugRobot::setCustomData(const std::string& inputString){
    customData->setSFString(inputString);
}


bool RugRobot::collAvoid() {
    for (std::size_t i = 0; i < n_sensors; ++i) {
        if (d_distance_sensors[i]->getValue() < CA_Threshold) {
            return true;
        }
    }
    return false;
}

void RugRobot::setSpeed(double speedl, double speedr) {
    speedl = std::clamp(speedl, -100.0, 100.0);
    speedr = std::clamp(speedr, -100.0, 100.0);

    leftMotor->setVelocity(speedl / 100 * (1 - motor_dev) * speed_dev * 10);
    rightMotor->setVelocity(speedr / 100 * (1 + motor_dev) * speed_dev * 10);
}

int RugRobot::turnAngle(double Angle) {
    double Pgain = 2.5;
    double Igain = 0.1;
    double dt = timeStep / 1000.0;
    double e = Angle - refAngle;
    double gyro_val_z = gyro->getValues()[2] * 180 / M_PI;
    angleIntegrator += e * dt;
    refAngle += gyro_val_z * dt;
    if (std::abs(e) > 2.5) {
        double left = -Pgain * e - Igain * angleIntegrator;
        double right = Pgain * e + Igain * angleIntegrator;
        setSpeed(left, right);
        return 0;
    } else {
        clearAngle();
        setSpeed(0, 0);  
        return 1;
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

void RugRobot::generateRW(){
    rw_time =rw_time_gen(generator);
    rw_angle = rw_angle_gen(generator);
    rw_time = std::clamp(rw_time,1000.0,20000.0);
    //std::cout<<"RW parameters= "<<rw_time<<',' <<rw_angle<<'\n';
    state = STATE_PAUSE;
    
}   

int RugRobot::RandomWalk(){

    if (spend_time == (double) timeStep){state= STATE_FW;}
    spend_time+= (double) timeStep;



    if ((spend_time > rw_time) && (state == STATE_FW)){
        state = STATE_TURN;
        //std::cout <<"TURN state"<<'\n';
        }

    if (collAvoid() && state==STATE_FW){
        state = STATE_CA;
        //std::cout <<"CA state"<<'\n';
    }
    if (state == STATE_CA){
        if(turnAngle(ca_angle)==1){
            //std::cout <<"CA state exit"<<'\n';
            state = STATE_FW;
            ca_angle = ca_angle_gen(generator);
        }
    }

    if (state == STATE_FW){
        setSpeed(100,100);
        }

    else if (state == STATE_TURN){
        if(turnAngle(rw_angle)==1){
            //std::cout <<"TURN state exit"<<'\n';
            state = STATE_RESET;
        }}
    if (state == STATE_RESET){
        spend_time = 0;
        generateRW();
        return 1;
    }
    return 0;

    }

std::vector<int>RugRobot::getPos() {
    std::vector<int> pos;
    const double *coordinates = translationData->getSFVec3f();
    const double xPos = coordinates[0];
    const double yPos = coordinates[2];

    pos.push_back((int) (xPos*100));
    pos.push_back((int) (yPos*100));
    //std::cout<<pos[0]<<","<<pos[1]<<'\n';
    return pos;
}





#endif // INCLUDED_RUGBOT_HH_
