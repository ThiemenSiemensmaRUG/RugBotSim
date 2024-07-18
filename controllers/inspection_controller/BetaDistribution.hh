
#include <iostream>
#include <fstream>
#include <vector>
#include <complex>
#include <vector>
#include <cmath>
#include <utility>
#include <filesystem>
class BetaDistribution {
public:
    int alpha_0;
    int beta_0;
    int alpha;
    int beta;
    // Constructor
    BetaDistribution(int a0, int b0) 
        : alpha_0(a0), beta_0(b0), alpha(a0), beta(b0) {}

    void update(int sample);
    double getMode();
    double getMean();
    double getBelief();
    double getCDF(double a, double b, double x) ;

private:
    float const tinyNr = 1.0e-30;
    float const stopNr = 1.0e-8;
};

void BetaDistribution::update(int sample) {
    beta += (1-sample);
    alpha+= (sample);
}

double BetaDistribution::getMode(){
    return (((double) alpha) - 1) / (((double) alpha)+((double) beta) - 2);
}

double BetaDistribution::getMean(){
    return (double) alpha / ( (double) alpha+ (double) beta);
}

double BetaDistribution::getBelief(){

    return getCDF((double) alpha,(double) beta,0.5);
}


double BetaDistribution::getCDF(double a, double b, double x) {
    if (x < 0.0 || x > 1.0) return 1.0/0.0;

    /*The continued fraction converges nicely for x < (a+1)/(a+b+2)*/
    if (x > (a+1.0)/(a+b+2.0)) {
        return (1.0-BetaDistribution::getCDF(b,a,1.0-x)); /*Use the fact that beta is symmetrical.*/
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
