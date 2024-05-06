#ifndef INCLUDED_ROVABLE_H_
#define INCLUDED_ROVABLE_H_

#include <algorithm>
#include <webots/DistanceSensor.hpp>
#include <webots/Emitter.hpp>
#include <webots/Robot.hpp>
#include <webots/Supervisor.hpp>
#include <webots/Motor.hpp>
#include <webots/Gyro.hpp>
#include <stdio.h>      /* printf, NULL */
#include <stdlib.h>     /* srand, rand */
#include <time.h>       /* time */
#include <chrono>
#include <iostream>
#include <environment.hh>
#include <radio.hh>
#include <parameters.hh>
#include <random>


#define MAX_SPEED 12;

using namespace webots;


// Class definition for Rover
class Rover {
    enum States 
    {
        STATE_RW,                       // State: Random Walk
        STATE_CA,                       // State: Collision Avoidance
        STATE_OBS,                      // State: Observe Color
        STATE_PAUSE,                    // etc....
        STATE_PULL,
        STATE_SEND,
        STATE_RESET,
        STATE_RESET_CA,
    };
    
    States state = STATE_RW;            // Starting state
    Supervisor *d_robot;                // Webots Supervisor instance
    Environment d_arena;                // Environment instance
    Motor *leftMotor;                   // Left motor
    Motor *rightMotor;                  // Right motor
    Gyro *gyro;                         // Gyro sensor
    Radio_Rover d_msgHandler;           // Radio_Rover instance for communication
    Node *d_this_robot_node;            // Node representing the current robot
    Field *d_locationField;             // Field for obtaining robot's translation
    Field *myDataField;                 // Custom data field for the robot
    AlgorithmParameters d_algParameters;// Algorithm parameters instance

    // Constants and variables for sensors and motors
    std::size_t static const n_sensors = 3;
    char const *distance_sensors_names[n_sensors] = {
        "left distance sensor", 
        "right distance sensor", 
        "middle distance sensor"
    };
    DistanceSensor *d_distance_sensors[n_sensors];

    char const *dMotorNames[2] = {"left motor", "right motor"};
    int pauseCount = 500;               // Initial pause count
    int walk_Time = 1000;               // Walk time duration
    int CA_counter = 2000;              // Collision avoidance counter
    std::size_t last_time_sent = 0;     // Last time a message was sent
    double refSpeed = 100;              // Reference speed
    double maxSpeed = 100;              // Maximum speed
    double minSpeed = 30;               // Minimum speed
    double angle = 90;                  // Angle value
    double ref_angle = 0;               // Reference angle
    double angle_integrator = 0;        // Angle integrator
    int final_dec_flag = 1;             // Final decision flag
    int SeedRov = 0;                    // Seed value for the random number generator
    int tau_flag = 0;                   // Tau flag for certain conditions

    const long max_rand = 1000000L;     // Maximum value for random number generation

    // Bounds and deviation values
    double lower_bound_angle = -0.125;
    double upper_bound_anlge = 0.125;
    double lower_bound_speed = 0.95;
    double upper_bound_speed = 1.05;

    double motor_dev = 0;
    double speed_dev = 0;
    int use_var_send = 0;
    double var_beta = 1;
    double scaling_fac =1;
    double alpha_d = 1;
    double beta_d =1;
    int spend_time = 0;                 // Time spent in a particular state
    int mess_ = 0;

public:
    // Constructor
    Rover(Environment &arena);
    
    // Destructor
    ~Rover();
    
    // Time step for the simulation
    enum {TIME_STEP = 20};

    // Main function to execute the robot's behavior
    void run();

    // Function to handle the pause state
    void pause(int *pauseCount);

    // Function to set motor speeds
    void setSpeed(double speedl, double speedr);

    // Function to turn the robot by a specified angle
    void turnAngle(double Angle, double *refAngle, double *angleIntergrator);

    // Function to clear the reference angle and angle integrator
    void clearAngle(double *refAngle, double *angleIntergrator);

    // Function to control walking time and target angle
    void walkTime(std::size_t *controlCount, int *walkTime, double tAngle);

    // Function for collision avoidance
    bool collAvoid();

    // Function to set collision avoidance speed
    double setCollSpeed(double val);

    // Function to perform collision avoidance
    void doCollAvoid(int *CA_counter);

    // Function to receive messages
    void receiveMessage();

    // Function to send messages
    void sendMessage();

        // Function to send messages
    void sendMessage_p(int mess);

    // Function to observe color
    void observeColor();
};

// Constructor implementation
Rover::Rover(Environment &arena):
    d_arena(arena)
{
    // Initialize Webots Supervisor
    d_robot = new Supervisor();

    // Initialize distance sensors
    for (std::size_t i = 0; i < n_sensors; ++i) 
    {
        d_distance_sensors[i] = d_robot->getDistanceSensor(distance_sensors_names[i]);
        d_distance_sensors[i]->enable(TIME_STEP);
    }

    // Initialize motors
    leftMotor = d_robot->getMotor(dMotorNames[0]);
    rightMotor = d_robot->getMotor(dMotorNames[1]);
  
    leftMotor->setPosition(INFINITY);
    rightMotor->setPosition(INFINITY);
    leftMotor->getMaxTorque();
    
    leftMotor->setVelocity(0);
    rightMotor->setVelocity(0);

    // Initialize robot-related fields and sensors
    d_this_robot_node = d_robot->getSelf();
    d_locationField = d_this_robot_node->getField("translation");
    myDataField = d_this_robot_node->getField("customData");
    
    gyro = d_robot->getGyro("gyro");
 
    gyro->enable(TIME_STEP);
    d_msgHandler = Radio_Rover(d_robot, TIME_STEP);
    d_algParameters.readParameters();
    
    // Display experiment parameters
    if(true){
        std::cout << "Running experiment with:" <<'\n';
        std::cout << "RWmean = " << d_algParameters.RWmean << '\n';
        std::cout << "RWstde = " << d_algParameters.RWvariance << '\n';
        std::cout << "tau = " << d_algParameters.tao << '\n';
        std::cout << "Uplus = " << d_algParameters.uPlus << '\n';
        std::cout << "p_c = " << d_algParameters.p_c << '\n';
        std::cout << "CAthreshold = " << d_algParameters.CAmax << '\n';
        std::cout << "d_f min count = " << d_algParameters.p_c_count_threshold << '\n';
    };
}

// Destructor implementation
Rover::~Rover(){
    delete d_robot;
}


/*
 * Function: run
 * Description: Main function to execute the robot's behavior. Handles different states and performs actions accordingly.
 */
void Rover::run() {
    std::size_t controlCount = 0; 
    std::size_t resetCount = 0; 



    std::ifstream file("settings.txt");
    int z;
    for (int i = 0; i < 2; i++) {
        std::string line;
        std::getline(file, line);
        const char *cstr = line.c_str();
        z = std::atof(cstr);
        if (i == 0){use_var_send = z;}
        std::cout<<"use var send = "<<use_var_send<<'\n';
        }

    std::string name = d_robot->getName();
    SeedRov = name[1];
    srand(SeedRov);
    std::default_random_engine generator (SeedRov*10);

    std::cauchy_distribution<double> cauchy(d_algParameters.RWmean,d_algParameters.RWvariance);
    
    // Display information about random numbers and parameters
    std::cout << "SEED num angle->" << rand() <<'\n';
    std::cout << "SEED num RW->" << generator <<'\n';
    std::cout << "num RW->" << cauchy(generator) <<'\n';
    std::cout << "num ANG->" << 180 - (rand() % 361) <<'\n';

    // Set walk time and angle based on random values
    walk_Time = cauchy(generator);
    walk_Time = std::clamp(walk_Time, 1000, 12000);
    angle = 180 - (rand() % 361);

    //random generator for messages
    std::random_device rd_prob;
 
    std::bernoulli_distribution message_prob_sent;

    // Set motor deviations based on random values
    motor_dev = lower_bound_angle
                 + (upper_bound_anlge - lower_bound_angle)
                 * (random() % max_rand)
                 / max_rand;
    speed_dev = lower_bound_speed
                 + (upper_bound_speed - lower_bound_speed)
                 * (random() % max_rand)
                 / max_rand;

    std::cout << "Motor deviations[a,s]:" << motor_dev << ',' << speed_dev << '\n';

    // Main simulation loop
    while(d_robot->step(TIME_STEP) != -1) {
        switch(state) {
            case STATE_CA:
                // Perform collision avoidance
                doCollAvoid(&CA_counter);
                // Update collision time
                d_algParameters.collisionTime = d_algParameters.collisionTime + TIME_STEP;
                break;
            case STATE_RW:
                // Reset collision avoidance counter and pause count
                CA_counter = 2000;
                pauseCount = 1000;
                // Perform random walk with specified parameters
                walkTime(&controlCount, &walk_Time, angle);
                // Update walk time
                d_algParameters.walkTime = d_algParameters.walkTime + TIME_STEP;
                break;
            case STATE_OBS:
                // Observe color
                observeColor();
                break;
            case STATE_PAUSE:
                // Pause state
                pause(&pauseCount);
                break;
            case STATE_SEND:
                // Send message
                if (use_var_send==1){
                alpha_d = (double)(d_algParameters.alpha);
                beta_d = (double)(d_algParameters.beta);
                var_beta = (alpha_d *beta_d) / 
                ((alpha_d +beta_d)*(alpha_d +beta_d)* ((alpha_d + beta_d+1.0)));


                scaling_fac = exp(-1.0* ((double) (d_algParameters.p_c_count_threshold)) * var_beta) * std::abs(0.5 - d_algParameters.p)* std::abs(0.5 - d_algParameters.p);
                
                d_algParameters.message_prob =( 1.0-d_algParameters.p ) * (scaling_fac) + ((double) d_algParameters.observationColor) * (1.0-scaling_fac) ;

               
                std::cout << d_algParameters.message_prob<< '\n';
                message_prob_sent.param(std::bernoulli_distribution::param_type(d_algParameters.message_prob ));
            
                mess_ = (int) message_prob_sent(rd_prob);
                

               
 
                sendMessage_p(mess_);

                }
                else{
              
                sendMessage();}
                break;
            case STATE_PULL:
                // Receive message
                receiveMessage();
                break;
            case STATE_RESET:
                // Reset parameters for random walk
                walk_Time = cauchy(generator);
                walk_Time = std::clamp(walk_Time, 1000, 30000);
              
                angle = 180 - (rand() % 361);
                state = STATE_RW;
                d_algParameters.RWcount += 1;
                resetCount += 1;
                //spend_time = 0;
                break;
            case STATE_RESET_CA:
                // Reset parameters for collision avoidance
                angle = 180 - (rand() % 361);
                state = STATE_RW;
                //spend_time = 0;
                break;
        }

        // Update decision time if decision flag is not -1 and final decision flag is not 0
        if((d_algParameters.decisionFlag != -1) && (final_dec_flag != 0)) {
            d_algParameters.decisionTime = d_algParameters.decisionCounterTime;
            final_dec_flag = 0;
        }

        // Update custom data field with algorithm parameters
        myDataField->setSFString(
            std::to_string(d_algParameters.p) + "," +
            std::to_string(d_algParameters.decisionFlag) + "," +
            std::to_string(d_algParameters.alpha) + "," +
            std::to_string(d_algParameters.beta) + "," +
            std::to_string(d_algParameters.observationCount) + "," +
            std::to_string(d_algParameters.onboard_alpha) + "," +
            std::to_string(d_algParameters.onboard_sample_count) + "," +
            std::to_string(d_algParameters.swarmRecv) + "," +
            std::to_string(d_algParameters.swarmSend) + "," +
            std::to_string(d_algParameters.RWcount) + "," +
            std::to_string(d_algParameters.collisionTime) + "," +
            std::to_string(d_algParameters.walkTime) + "," +
            std::to_string(d_algParameters.decisionTime)
        );

        // Update decision counter time
        d_algParameters.decisionCounterTime += TIME_STEP;

        // Decision flag == 0 equals black, decision flag == 1 equals white.
        // We need black, so 0 decision/observation, but 1 as belief.
    }
    return;
}

/*
 * Function: pause
 * Description: Pauses the robot's movement for a specified duration.
 * Parameters:
 *   - pause_Time: Pointer to the remaining pause time.
 */
void Rover::pause(int *pause_Time) {
    // Stop the robot's movement
    setSpeed(0, 0);
    
    // Check if pause time has elapsed, if yes, transition to observation state
    if (*pause_Time <= 0) {
        state = STATE_OBS;
        return;
    }
    
    // Decrease pause time based on the time step
    *pause_Time = *pause_Time - 1 * TIME_STEP;
};

/*
 * Function: setSpeed
 * Description: Sets the motor speeds of the robot while considering speed constraints.
 * Parameters:
 *   - speedl: Left motor speed.
 *   - speedr: Right motor speed.
 */
void Rover::setSpeed(double speedl, double speedr) {   
    // Apply speed constraints
    if ((speedl / 10) > 10) { speedl = 100; };
    if ((speedl / 10) < -10) { speedl = -100; };
    if ((speedr / 10) > 10) { speedr = 100; };
    if ((speedr / 10) < -10) { speedr = -100; };

    // Set motor velocities with deviations
    leftMotor->setVelocity(speedl / 100 * (1 - motor_dev) * speed_dev * 10);
    rightMotor->setVelocity(speedr / 100 * (1 + motor_dev) * speed_dev * 10);
};

/*
 * Function: collAvoid
 * Description: Checks if the robot is close to an obstacle using distance sensors for collision avoidance.
 * Returns: True if collision is detected, false otherwise.
 */
bool Rover::collAvoid() {
    for (std::size_t i = 0; i < n_sensors; ++i) {
        if (d_distance_sensors[i]->getValue() < d_algParameters.CAmax) {
            return true;
        }
    }
    return false;
}

/*
 * Function: setCollSpeed
 * Description: Calculates the collision avoidance speed based on a specified value.
 * Parameters:
 *   - val: Current value to calculate collision avoidance speed.
 * Returns: Calculated collision avoidance speed.
 */
double Rover::setCollSpeed(double val) {
    double r = (refSpeed) / (d_algParameters.CAmax);
    
    if ((val <= d_algParameters.CAmax) && (val > d_algParameters.CAmin)) {
        return r * val - r * d_algParameters.CAmin;
    }
    
    if (val <= d_algParameters.CAmin)
        return 0;
    else
        return refSpeed;
}

/*
 * Function: doCollAvoid
 * Description: Performs actions related to collision avoidance. Currently, it turns the robot by a specified angle.
 * Parameters:
 *   - CA_counter: Counter for collision avoidance actions.
 */
void Rover::doCollAvoid(int *CA_counter) {
    // Turn the robot by the specified angle
    turnAngle(angle, &ref_angle, &angle_integrator);
}

/*
 * Function: walkTime
 * Description: Manages the time the robot spends in the random walk state.
 * Parameters:
 *   - controlCount: Pointer to the control count.
 *   - walkTime: Pointer to the remaining walk time.
 *   - tAngle: Target angle for turning.
 */
void Rover::walkTime(std::size_t *controlCount, int *walkTime, double tAngle) {
    // Reset collision avoidance counter
    CA_counter = 2000;
    
    // Increment control count and spend time
    *controlCount += TIME_STEP; 
    spend_time += TIME_STEP;
    
    // Check if it's time to pause and transition to the pause state
    if (((spend_time) % d_algParameters.tao > (d_algParameters.tao - (TIME_STEP + 1))) && (*walkTime > 0)) { 
        last_time_sent = *controlCount;
        state = STATE_PAUSE;
        return;
    } 
    
    // Check if walk time has elapsed, if yes, turn the robot by the target angle
    if (*walkTime <= 0) {   
        turnAngle(tAngle, &ref_angle, &angle_integrator);
        return;
    }
    
    // Check for collision avoidance, transition to the collision avoidance state if necessary
    if (collAvoid()) {
        state = STATE_CA;
    } else {
        // Set constant speed in the random walk state
        setSpeed(refSpeed, refSpeed);
    }

    // Decrease walk time based on the time step
    *walkTime = *walkTime - 1 * TIME_STEP;
};

/*
 * Function: turnAngle
 * Description: Turns the robot by a specified angle using a proportional-integral controller.
 * Parameters:
 *   - Angle: Target angle to turn towards.
 *   - refAngle: Pointer to the reference angle.
 *   - angleIntergrator: Pointer to the angle integrator.
 */
void Rover::turnAngle(double Angle, double *refAngle, double *angleIntergrator) {
    // Proportional and integral gains
    double Pgain = 2.5;
    double Igain = 0.1;
    double dt = TIME_STEP / 1000.0;
    double e = 0;
    
    // Calculate error
    e = (Angle) - *refAngle;

    // Get gyro reading and convert to degrees
    double gyro_val_z = gyro->getValues()[2];
    gyro_val_z = gyro_val_z * 180 / 3.1415;

    // Update angle integrator
    *angleIntergrator += e * dt;
    *refAngle += (gyro_val_z * dt);

    // Apply control law if error is large enough, otherwise reset parameters
    if (abs(e) > (2.5)) {
        double left = -Pgain * e  - Igain * *angleIntergrator;
        double right = Pgain * e + Igain * *angleIntergrator;
        right = right * 1.5;
        left = left * 1.5;
        setSpeed(left, right);
    } else {
        clearAngle(&ref_angle, &angle_integrator);
        setSpeed(0, 0);
        // Transition to reset state based on the current state
        if (state == STATE_RW) {
            state = STATE_RESET;
        }
        if (state == STATE_CA) {
            state = STATE_RESET_CA;
        }
    }
};

/*
 * Function: clearAngle
 * Description: Resets the reference angle and angle integrator.
 * Parameters:
 *   - refAngle: Pointer to the reference angle.
 *   - angleIntergrator: Pointer to the angle integrator.
 */
void Rover::clearAngle(double *refAngle, double *angleIntergrator) {
    *refAngle = 0;
    *angleIntergrator = 0;
};

/*
 * Function: receiveMessage
 * Description: Receives messages from other robots in the swarm, updates algorithm parameters.
 */
void Rover::receiveMessage() {
    // Get messages from the message handler
    std::vector<int> messages = d_msgHandler.getMessages();
   
    // Process received messages
    for (int cPrime : messages) {
        d_algParameters.alpha += cPrime;   
        d_algParameters.beta += (1 - cPrime);
        d_algParameters.swarmRecv = d_algParameters.swarmRecv + 1;
    }
    
    // Update probability based on received information
    d_algParameters.updateP();
    
    // Transition to random walk state
    state = STATE_RW;
    
}

/*
 * Function: sendMessage
 * Description: Sends a message to other robots in the swarm.
 */
void Rover::sendMessage() {
    // Determine the message to send based on decision flag or observation color
    int const *message;
    if (d_algParameters.decisionFlag != -1 && d_algParameters.uPlus) {
        message = &d_algParameters.decisionFlag;
    } else {
        message = &d_algParameters.observationColor;
    }
    
    // Send the message
    d_msgHandler.sendMessage(message, sizeof(message));
    
    // Update swarm send counter
    d_algParameters.swarmSend = d_algParameters.swarmSend + 1;
    
    // Transition to message pull state
    state = STATE_PULL;
}

void Rover::sendMessage_p(int mess) {
    //std::cout << 'message = ' << &mess<<'\n';
    int const *message = &mess;
    // Send the message
    d_msgHandler.sendMessage(message, sizeof(message));
    
    // Update swarm send counter
    d_algParameters.swarmSend = d_algParameters.swarmSend + 1;
    
    // Transition to message pull state
    state = STATE_PULL;
}

/*
 * Function: observeColor
 * Description: Observes the color of the environment at the robot's current position.
 * Updates algorithm parameters based on the observation.
 */
void Rover::observeColor() {
    // Get current coordinates
    const double *coordinates = d_locationField->getSFVec3f();
    const double xPos = coordinates[0];
    const double yPos = coordinates[2];
    
    // Obtain color information from the environment
    bool color = d_arena.getColor(xPos, yPos);
    // Update observation and alpha, beta values
    d_algParameters.observationColor = color;
    d_algParameters.alpha += color;
   
    d_algParameters.beta += (1 - color);
    
    
    // Update probability based on observation
    d_algParameters.updateP();
    
    // Increment observation count
    d_algParameters.observationCount += 1;
    

    if (use_var_send==1){
    
           // Check if the observation count is greater than the threshold to make a decision
        if (d_algParameters.observationCount > 85) {

            if (d_algParameters.p > d_algParameters.p_c) {
                // Decision: Black
                d_algParameters.decisionFlag = 0;
                std::cout << "1 Decision made =  " << d_algParameters.decisionFlag << '\n';
            } else if ((1 - d_algParameters.p) > d_algParameters.p_c) {
                // Decision: White
                d_algParameters.decisionFlag = 1;
                std::cout << "1 Decision made =  " << d_algParameters.decisionFlag << '\n';
            }
    }
    }
    else{

        // Check if the observation count has reached the threshold
        if (d_algParameters.observationCount == d_algParameters.p_c_count_threshold) {
            std::cout << "Passed the count threshold at " << d_robot->getTime() << '\n';
        }
        


        // Check if the observation count is greater than the threshold to make a decision
        if (d_algParameters.observationCount > d_algParameters.p_c_count_threshold &&d_algParameters.decisionFlag == -1 ) {

            if (d_algParameters.p > d_algParameters.p_c) {
                d_algParameters.onboard_sample_count = d_algParameters.alpha + d_algParameters.beta;
                d_algParameters.onboard_alpha = d_algParameters.alpha;
                // Decision: Black
                d_algParameters.decisionFlag = 0;
                std::cout << "0 Decision made =  " << d_algParameters.decisionFlag << '\n';
            } else if ((1 - d_algParameters.p) > d_algParameters.p_c) {
                // Decision: White
                d_algParameters.onboard_sample_count = d_algParameters.alpha + d_algParameters.beta;
                d_algParameters.onboard_alpha = d_algParameters.alpha;
                d_algParameters.decisionFlag = 1;
                std::cout << "0 Decision made =  " << d_algParameters.decisionFlag << '\n';
            }
            if(d_algParameters.decisionFlag ==-1){
                d_algParameters.onboard_sample_count = d_algParameters.alpha + d_algParameters.beta;
                d_algParameters.onboard_alpha = d_algParameters.alpha;

            }
        }
    }
    // Update last measured color for debugging purposes
    d_algParameters.lastMeasuredC = static_cast<int>(color);
    
    // Transition to message send state
    state = STATE_SEND;      
    return;
};




#endif
