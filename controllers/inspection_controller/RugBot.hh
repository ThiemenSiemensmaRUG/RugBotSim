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

    int SeedRov = 0;

    double timeStep;
    double rw_time;
    double rw_angle;
    double ca_angle;
    double spend_time;
    int CAtime = 0;
    int RWtime = 0;

    double CA_Threshold = 60.0;
    std::size_t static const n_sensors = 3;
    const char *distance_sensors_names[n_sensors] = {
        "left distance sensor", 
        "right distance sensor", 
        "middle distance sensor"
    };
    DistanceSensor *d_distance_sensors[n_sensors];
    const char *dMotorNames[2] = {"left motor", "right motor"};


    double speed_dev = 1;
    double motor_dev = 0;
    double battery_drain = 1;//1 = 100%


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
        STATE_IDLE,
    };

    RStates state = STATE_FW;

    std::default_random_engine generator;

    std::uniform_real_distribution<double> angle_dist;
    std::gamma_distribution<double> speed_dist;

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
    void setState(RStates newState);
    void generateRW();
    void setCustomData(const std::string& inputString);
    std::vector<double> getPos();
    void setRWTimeGenParams(double location, double scale);
    void setAngleDistParams(double lower_bound, double upper_bound);
    void setSpeedDistParams(double shape, double scale, double location);
    void setRandomizationSpeed();
    void setSeeds(int seed);
};




RugRobot::RugRobot(double timeStep) : timeStep(timeStep) {
    d_robot = new Supervisor();



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
    SeedRov = ((int) name[1]) * 10;
    srand(SeedRov);
    generator.seed(SeedRov);
    
    rw_angle_gen =  std::uniform_real_distribution<double>(-180.0, 180.0);
    ca_angle_gen =  std::uniform_real_distribution<double>(-180.0, 180.0);
    
    
    setRWTimeGenParams(15000.0,0.0);
    setAngleDistParams(0,0);
    setSpeedDistParams(3.48249,0.72997,1);


    ca_angle = ca_angle_gen(generator);
    motor_dev = angle_dist(generator);
    speed_dev = speed_dist(generator);

    //std::cout << "Motor deviations[a,s]:" << motor_dev << ',' << speed_dev << '\n';
}
// Destructor definition
RugRobot::~RugRobot() {
    // Clean up dynamically allocated sensors
    for (std::size_t i = 0; i < n_sensors; ++i) {
        delete d_distance_sensors[i];
    }

    // Clean up dynamically allocated motors
    delete leftMotor;
    delete rightMotor;
    
    // Clean up other Webots objects if they are dynamically allocated
    delete gyro;
    delete d_robot;
    delete emitter;
    delete receiver;

    // If any other resources were allocated dynamically, clean them up here
}

void RugRobot::setSeeds(int seed){
    std::cout << "input seed = "<< seed<<'\n';
    std::string name = d_robot->getName();
    SeedRov = ((int) name[1] +1) * 1234;
    generator.seed(SeedRov * seed);
    
    srand(SeedRov * seed);
    std::cout << "RugRobot " << name[1] << " with Seed " << SeedRov * seed <<","  << rw_angle_gen(generator)<<'\n';
}

void RugRobot::setRWTimeGenParams(double location, double scale) {
    rw_time_gen = std::cauchy_distribution<double>(location, scale);
    std::cout << "new random walk paramters loc, scale "<<location <<","<<scale<<'\n'; 
    generateRW();
}


void RugRobot::setAngleDistParams(double lower_bound, double upper_bound) {
    
    angle_dist = std::uniform_real_distribution<double>(lower_bound, upper_bound);
    motor_dev = angle_dist(generator);
    
    std::cout<<"new angle distribution parameters: "<<motor_dev<<"\n";
}

void RugRobot::setSpeedDistParams(double shape, double scale, double location) {
    
    speed_dist = std::gamma_distribution<double>(shape,scale);
    speed_dev = (speed_dist(generator) + location) ;
    speed_dev = std::clamp(speed_dev,.9,1.5);
    
    //std::cout<<"new speed distribution parameters: "<<speed_dev<<"\n";
}





void RugRobot::setCustomData(const std::string& inputString){
    customData->setSFString(inputString);
}

void RugRobot::setState(RStates newState) {
    state = newState;
}

bool RugRobot::collAvoid() {
    for (std::size_t i = 0; i < n_sensors; ++i) {
        if (d_distance_sensors[i]->getValue() < CA_Threshold) {
            
            return true;
        }
    }
    return false;
}

void RugRobot::setRandomizationSpeed() {


}

void RugRobot::setSpeed(double speedl, double speedr) {
    speedl = std::clamp(speedl, -100.0, 100.0);
    speedr = std::clamp(speedr, -100.0, 100.0);

    
    leftMotor->setVelocity(speedl / 100 * (1 - motor_dev) * speed_dev * battery_drain * 10);
    rightMotor->setVelocity(speedr / 100 * (1 + motor_dev) * speed_dev * battery_drain * 10);
}

int RugRobot::turnAngle(double Angle) {
    double Pgain = 2.5;
    double Igain = 0.15;
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
    rw_time = std::clamp(rw_time,1000.0,30000.0);
    state = STATE_PAUSE;

    
}   

int RugRobot::RandomWalk(){


    if (spend_time < (timeStep-1)){state= STATE_FW;}
    RWtime+=timeStep;

    if ((spend_time > rw_time) && (state == STATE_FW)){
        state = STATE_TURN;
        }

    if (collAvoid() && state==STATE_FW){
        state = STATE_CA;

    }
    if (state == STATE_CA){
        
        CAtime+=timeStep;
        
        if(turnAngle(ca_angle)==1){
            state = STATE_FW;
            ca_angle = ca_angle_gen(generator);
            
        }
        
    }

    if (state == STATE_FW){
        spend_time+= (int) timeStep;
        setSpeed(100,100);
        return 2;
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

std::vector<double>RugRobot::getPos() {
    std::vector<double> pos;
    const double *coordinates = translationData->getSFVec3f();
    const double xPos = coordinates[0];
    const double yPos = coordinates[2];

    pos.push_back((double) (xPos));
    pos.push_back((double) (yPos));

    return pos;
}





#endif // INCLUDED_RUGBOT_HH_
