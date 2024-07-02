
#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <utility>



class eigenFreq {

    private:
        float const tinyNr = 1.0e-30;
        float const stopNr = 1.0e-8;
        double alpha_0 =0;
        double beta_0=0;



        double mode = 0;
        double mean = 0;
        std::vector<double> filtered ;
        std::vector<double> unfiltered;


    public:
        std::vector<double> b = { 0.15, 0.15};//{0.00779294, 0.00779294};//
        std::vector<double> a ={ 1.   ,      -0.96}; //{1,-0.98441413};//
        double alpha = 0;
        double beta =0;
        double upper_freq = 100.0;
        double learning_rate = 1;


        eigenFreq(double alpha_0 = 1.0, double beta_0 = 1.0, double upper_freq = 100.0) 
        : alpha_0(alpha_0), beta_0(beta_0), upper_freq(upper_freq), alpha(alpha_0), beta(beta_0), mode(0), mean(0) {};


        int iteration = 0;

        void update(int sample);
        double BetaCDF(double alpha,double beta);
        double getGeomMean();
        double getMode();
        double iBeta(double a, double b, double x);
        double getEstimatedFreq();
        int checkSample(double sample);
        double getAlpha();
        double getBeta();
        

};



// eigenFreq::eigenFreq(double alpha_0 = 0, double beta_0 = 0, double upper_freq = 100) 
//         : alpha_0(alpha_0), beta_0(beta_0), upper_freq(upper_freq), alpha(1), beta(1), mode(0), mean(0.5) {}


double eigenFreq::getGeomMean(){
    return (alpha - 1/2) / (alpha+ beta - 1/2) * upper_freq;
};

double eigenFreq::getMode(){
    return ((alpha-1) / (alpha+beta-2)) ;
};

void eigenFreq::update(int sample){

    if (sample ==1){
        beta += beta / (beta + alpha) * learning_rate;
    }
    else{
        alpha += alpha / (beta + alpha) * learning_rate;
    }    

    

    if (iteration>2){
        unfiltered.push_back(getMode());

        filtered.push_back(b[0] * unfiltered[iteration]);
        for (int j = 1; j < b.size(); ++j) {
                filtered[iteration] += b[j] * unfiltered[iteration - j];
                filtered[iteration] -= a[j] * filtered[iteration-j];
                
            }

     
    }
    else{
        unfiltered.push_back(getMode());
        filtered.push_back(getMode() );
    }


    iteration+=1;

    


    iBeta(alpha,beta,0.5);

};



double eigenFreq::getEstimatedFreq(){
    
    if (iteration <3){

        return getMode() * upper_freq;
    }

    else{return filtered[iteration-1] * upper_freq ;}
    
};

double eigenFreq::getAlpha(){
    return alpha;
}
double eigenFreq::getBeta(){
    return beta;
}

int eigenFreq::checkSample(double sample){
    
    if ((sample) < getEstimatedFreq()){return 1;}
    else{return 0;}
}

double eigenFreq::iBeta(double a, double b, double x) {
    if (x < 0.0 || x > 1.0) return 1.0/0.0;

    /*The continued fraction converges nicely for x < (a+1)/(a+b+2)*/
    if (x > (a+1.0)/(a+b+2.0)) {
        return (1.0-eigenFreq::iBeta(b,a,1.0-x)); /*Use the fact that beta is symmetrical.*/
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





