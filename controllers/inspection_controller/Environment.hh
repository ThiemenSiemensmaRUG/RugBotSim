#ifndef INCLUDED_ARENA_H_
#define INCLUDED_ARENA_H_

#include <exception>
#include <fstream>
#include <iostream>
#include <string>
#include <sstream>
#include <vector>
#include <random>

char *wPath = getenv("WB_WORKING_DIR");

/**
 * @brief Represents an environment with a grid of tiles.
 * 
 * The Environment class manages data about the environment, including a filename,
 * a grid of tile coordinates, and a DEBUG flag for debugging.
 */
class Environment {
    std::string filename;                         ///< The name of the file containing environment data.
    std::vector<std::pair<int, int>> d_grid;      ///< The grid of tile coordinates.

public:
    int d_nrTiles = 5;       ///< The constant number of tiles.

    Environment(std::string file);
    ~Environment();

    /**
     * @brief Retrieves the color of the tile at the specified coordinates.
     * 
     * This function takes x and y coordinates as input and returns an integer value indicating the color of the tile.
     * The implementation details of determining the color are not provided in this comment.
     * 
     * @param x The x-coordinate of the tile.
     * @param y The y-coordinate of the tile.
     * @param method_read The method to read the observation: 0 for using grid data, 1 for using distributions.
     * @return An integer value representing the color of the tile (1 for white, 0 for black).
     */
    int getSample(double x, double y);

    // Set the seed for the random number generator
    void setSeed(unsigned int seed);

    // Set distributions with location information
    void setVibDistribution(double shape, double scale, double location);
    void setNonVibDistribution(double shape, double scale, double location);
    void setFPdist(int fp_prob);
    void setFNdist(int fn_prob);
    int method_read = 0;
    double vibThresh = 1.33;
    double lastSample = 0;


private:
    // Distributions with location information
    std::gamma_distribution<double> d_vibDist; // Gamma distribution for vibration
    double d_vibLoc; // Location parameter for vibration distribution

    std::gamma_distribution<double> d_nonVibDist; // Gamma distribution for non-vibration
    double d_nonVibLoc; // Location parameter for non-vibration distribution

    std::bernoulli_distribution bernoulli_FP;

    std::bernoulli_distribution bernoulli_FN;

    



    std::mt19937 d_gen_environment; // Random number generator

    /**
     * @brief Reads data from a file and populates the environment's grid.
     * 
     * This private function is called internally by the constructor to read data from a file
     * and populate the 'd_grid' member variable.
     * 
     * @throws std::ios_base::failure if the file cannot be opened.
     */
    void readFile();
};

Environment::Environment(std::string file) : filename(file) {
    // Read data from the file and populate the grid
    readFile();
}

void Environment::setFPdist(int fp_prob){
    bernoulli_FP.param(std::bernoulli_distribution::param_type(
        (double (fp_prob) / 100)
    ));
    std::cout << "Prob(FP) = " << bernoulli_FP.p() <<"\n";    
}

void Environment::setFNdist(int fn_prob){
    bernoulli_FN.param(std::bernoulli_distribution::param_type(
        (double (fn_prob) / 100)
    ));
    std::cout << "Prob(FN) = " << bernoulli_FN.p() <<"\n";  
}


void Environment::readFile() {
    std::ifstream file;
    if (wPath != NULL) {
        char file_name[256];
        std::cout << "Webots working dir enabled" << '\n';
        sprintf(file_name, "%s/world.txt", wPath);
        file.open(file_name);
    } else {
        file.open(filename);
    }

    if (!file.is_open())
        throw std::ios_base::failure("The file cannot be read");

    std::string line;
    while (std::getline(file, line)) {
        std::istringstream lineStream(line);
        int x, y;
        char comma;

        if (lineStream >> x >> comma >> y) {
            d_grid.push_back(std::make_pair(x, y));
            std::cout << x << y << "\n";
        } else {
            std::cout << "Unsupported file formatting in world file" << '\n';
        }
    }
    std::cout << std::endl;
    file.close(); // Close the file
}

void Environment::setSeed(unsigned int seed) {
    d_gen_environment.seed(seed);
    std::cout<<"environmental seed: " <<seed<<'\n';
}

void Environment::setVibDistribution(double shape, double scale, double location) {
    d_vibDist = std::gamma_distribution<double>(shape, scale);
    d_vibLoc = location;
}

void Environment::setNonVibDistribution(double shape, double scale, double location) {
    d_nonVibDist = std::gamma_distribution<double>(shape, scale);
    d_nonVibLoc = location;
}


int Environment::getSample(double x, double y) {
    if (method_read == 0) { // Use grid data
        for (std::pair<int, int> coloredTile : d_grid) {
            if (
                (x >= 1.0 * coloredTile.first / d_nrTiles) &&
                (x <= (1.0 * coloredTile.first + 1) / d_nrTiles) &&
                (y >= 1.0 * coloredTile.second / d_nrTiles) &&
                (y <= (1.0 * coloredTile.second + 1) / d_nrTiles)
            ) {
                lastSample = 1;

                return 1; // WHITE TILE
            }
        }
        lastSample = 0;
        return 0; // BLACK TILE
    }

    if (method_read == 2) { // Use grid data and FP / FN
        for (std::pair<int, int> coloredTile : d_grid) {
            if (
                (x >= 1.0 * coloredTile.first / d_nrTiles) &&
                (x <= (1.0 * coloredTile.first + 1) / d_nrTiles) &&
                (y >= 1.0 * coloredTile.second / d_nrTiles) &&
                (y <= (1.0 * coloredTile.second + 1) / d_nrTiles)
            ) {
                // Sample false negative (FN) with probability `fn_prob`
                if (bernoulli_FN(d_gen_environment)) {
                    lastSample = 0; // False negative: white classified as black
                    return 0; // BLACK TILE due to FN
                } else {
                    lastSample = 1; // True positive: white classified as white
                    return 1; // WHITE TILE
                }
            }
        }
        if (bernoulli_FP(d_gen_environment)) {
            lastSample = 1; // False positive: black classified as white
            return 1; // WHITE TILE due to FP
        } else {
            lastSample = 0; // True negative: black classified as black
            return 0; // BLACK TILE
        }
    }


    if (method_read == 1) { // Use distributions
        for (std::pair<int, int> coloredTile : d_grid) {
            
            if (
                (x >= 1.0 * coloredTile.first / d_nrTiles) &&
                (x <= (1.0 * coloredTile.first + 1) / d_nrTiles) &&
                (y >= 1.0 * coloredTile.second / d_nrTiles) &&
                (y <= (1.0 * coloredTile.second + 1) / d_nrTiles)
            ) {
                // Sample from vibration distribution and apply location shift
                lastSample = d_vibDist(d_gen_environment) + d_vibLoc;
                if (lastSample > vibThresh) {return 1;}
                else {return 0;}
            }
        }
        // Sample from non-vibration distribution and apply location shift
        lastSample = d_nonVibDist(d_gen_environment) + d_nonVibLoc;
        if (lastSample > vibThresh) {return 1;}
        else {return 0;}
    }

    return 0; // Exception case
}

// Destructor definition
Environment::~Environment() {
    // Default destructor generated by the compiler handles cleanup
}

#endif
