#ifndef INCLUDED_ALGORITHM_PARAMETERS_H_
#define INCLUDED_ALGORITHM_PARAMETERS_H_

// IMPORTNAT! EDIT YOUR INCLUDE PATH SETTINGS FOR BOTH THE IDE AND MAKEFILE. 
// IT IS INCLUDED IN THE FOLDER 'external_C++_sources'
// SO INCLUDE THIS IN THE MAKEFILE FOR EXAMPLE:
// INCLUDE = -I"C:\Users\marti\OneDrive\Documenten\IEM\IP\project\demo\external_C++_sources"
#include <iostream>
#include <fstream>

#include <string>


char *pPath = getenv("WB_WORKING_DIR");
struct AlgorithmParameters
{
    float const tinyNr = 1.0e-30;
    float const stopNr = 1.0e-8;
    int nParam = 7;//RWdist,RWvariance,angleVariance,tao,uplus,alpha/beta,p_c

    // WARNING: SHOULD BE CONST DATA MEMBERS
    std::size_t tao = 2000; //observation interval

    std::size_t turn = 50;
    std::size_t obsInitial = 0; // what is this?
    std::size_t nrRobots;

    int alpha_0 = 1;      // not sure if alpha could be negative
    int beta_0 = 1;
    int pauseTime = 33;
    double var;
    double message_prob;
    bool uPlus;
    double p_c;

    // non const data members (parameter values)
    double p;
    int alpha;
    int onboard_alpha;
    int onboard_sample_count;
    int beta;
    int decisionFlag;
    int decisionTime;
    int decisionCounterTime;
    int observationColor;
    int lastMeasuredC;
    int RWmean;
    int RWvariance;
    int angleVariance;


    // TODO: make 'set' and 'increment' functions
    std::size_t observationCount;       // the number of measurements of color made
    std::size_t swarmSend;              // the number of messages send to the swarm from this instance
    std::size_t swarmRecv;              // the number of received messages from the swarm
    std::size_t walkTime;
    std::size_t collisionTime;
    std::size_t RWcount;
    std::size_t CAmin;
    std::size_t CAmax;
    std::size_t p_c_count_threshold;
    

    AlgorithmParameters();
                                        // filename without JSON extension
    double incrementBeta(double a, double b, double x);
    void updateP();
    void readParameters();
};

inline AlgorithmParameters::AlgorithmParameters()
:
    // STANDARD PARAMETERS
    nrRobots(4),
    var(0),
    message_prob(0),
    uPlus(0),
    p_c(0.95),
    alpha(alpha_0),
    onboard_alpha(1),
    onboard_sample_count(2),
    beta(beta_0),
    decisionFlag(-1),
    decisionTime(0),
    decisionCounterTime(0),
    observationColor(0),
    lastMeasuredC(0),
    RWmean(2),
    RWvariance(3),
    angleVariance(3),
    observationCount(0),
    swarmSend(0),
    swarmRecv(0),
    walkTime(0),
    collisionTime(0),
    RWcount(0),
    CAmax(0),
    p_c_count_threshold(0)
{
    updateP();
};

double AlgorithmParameters::incrementBeta(double a, double b, double x) {
    if (x < 0.0 || x > 1.0) return 1.0/0.0;

    /*The continued fraction converges nicely for x < (a+1)/(a+b+2)*/
    if (x > (a+1.0)/(a+b+2.0)) {
        return (1.0-AlgorithmParameters::incrementBeta(b,a,1.0-x)); /*Use the fact that beta is symmetrical.*/
    }

    /*Find the first part before the continued fraction.*/
    const double lbeta_ab = lgamma(a)+lgamma(b)-lgamma(a+b);
    const double front = exp(log(x)*a+log(1.0-x)*b-lbeta_ab) / a;

    /*Use Lentz's algorithm to evaluate the continued fraction.*/
    double f = 1.0, c = 1.0, d = 0.0;

    int i, m;
    for (i = 0; i <= 200; ++i) {
        m = i/2;

        double numerator;
        if (i == 0) {
            numerator = 1.0; /*First numerator is 1.0.*/
        } else if (i % 2 == 0) {
            numerator = (m*(b-m)*x)/((a+2.0*m-1.0)*(a+2.0*m)); /*Even term.*/
        } else {
            numerator = -((a+m)*(a+b+m)*x)/((a+2.0*m)*(a+2.0*m+1)); /*Odd term.*/
        }

        /*Do an iteration of Lentz's algorithm.*/
        d = 1.0 + numerator * d;
        if (fabs(d) < tinyNr) d = tinyNr;
        d = 1.0 / d;

        c = 1.0 + numerator / c;
        if (fabs(c) < tinyNr) c = tinyNr;

        const double cd = c*d;
        f *= cd;

        /*Check for stop.*/
        if (fabs(1.0-cd) < stopNr) {
            return front * (f-1.0);
        }
    }

    return 1.0/0.0; /*Needed more loops, did not converge.*/
}

void AlgorithmParameters::updateP()
{
    p = incrementBeta(alpha, beta, 0.5);
} 

void AlgorithmParameters::readParameters()
{   
    char prob_name[256];
    sprintf(prob_name, "%s/prob.txt", pPath);
    
    //Dont set the parameters if the pointer is NULL
    if (pPath != NULL) {
        std::ifstream file(prob_name);
        double z;
        for (int i = 0; i < nParam; i++) {
            std::string line;
            std::getline(file, line);
            const char *cstr = line.c_str();
            z = std::atof(cstr);
            if (i == 0) RWmean = z;
            if (i == 1) RWvariance = z;
            if (i == 2) tao = z;
            if (i == 3) uPlus = z;
            if (i == 4){p_c=z;}
            if (i == 5){CAmax =z;}
            if (i == 6){p_c_count_threshold = z;}
        }
        file.close();
    }
    else{
        std::ifstream file("prob.txt");
        std::cout << "Not using PSO script" << '\n'; 
        double z;
        for (int i = 0; i < nParam; i++) {
            std::string line;
            std::getline(file, line);
            const char *cstr = line.c_str();
            z = std::atof(cstr);
            if (i == 0) RWmean = z;
            if (i == 1) RWvariance = z;
            if (i == 2) tao = z;
            if (i == 3) uPlus = z;
            if (i == 4){p_c=z;}
            if (i == 5){CAmax =z;}
            if (i == 6){p_c_count_threshold = z;}
        }
        file.close();
    }

}


#endif