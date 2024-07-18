#ifndef INCLUDED_ARENA_H_
#define INCLUDED_ARENA_H_

#include <exception>
#include <fstream>
#include <iostream>
#include <string>
#include <sstream>
#include <vector>

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

    /**
     * @brief Retrieves the color of the tile at the specified coordinates.
     * 
     * This function takes x and y coordinates as input and returns a boolean value indicating the color of the tile.
     * The implementation details of determining the color are not provided in this comment.
     * 
     * @param x The x-coordinate of the tile.
     * @param y The y-coordinate of the tile.
     * @param method_read The way to read the obesrvation, 0 for using world.txt, 1 for using abaqus data
     * @return A boolean value representing the color of the tile.
     */
    int getSample(double x, double y,int method_read);

private:
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

Environment::Environment(std::string file) {
    // Set the filename and DEBUG flag
    filename = file;
    // Print the filename for debugging purposes

    // Read data from the file and populate the grid
    readFile();
}
void Environment::readFile() {
    // Open the file for reading
    
    if (wPath != NULL) {
        char file_name[256];
        std::cout<< "webots working dir enabled" << '\n';
        sprintf(file_name, "%s/world.txt", wPath);
        std::ifstream file(file_name);
        // Check if the file is open
        if (!file.is_open())
            throw std::ios_base::failure("The file cannot be read");

        // Read each line from the file
        std::string line;
        while (std::getline(file, line)) {
            // Use a stringstream to parse the line
            std::istringstream lineStream(line);
            
            // Variables to store the parsed values
            int x, y;
            char comma;

            // Attempt to read x, comma, and y from the line
            if (lineStream >> x >> comma >> y) {
                // Store the pair (x, y) in the grid
                d_grid.push_back(std::make_pair(x, y));
                std::cout << x << y << '\n';

            } else {
                // Print a warning for unsupported file formatting
                std::cout << "Unsupported file formatting in world file" << '\n';
            }
        }
        }
        else{
            std::ifstream file(filename);
            if (!file.is_open())
            throw std::ios_base::failure("The file cannot be read");

            // Read each line from the file
            std::string line;
            while (std::getline(file, line)) {
                // Use a stringstream to parse the line
                std::istringstream lineStream(line);
                
                // Variables to store the parsed values
                int x, y;
                char comma;

                // Attempt to read x, comma, and y from the line
                if (lineStream >> x >> comma >> y) {
                    // Store the pair (x, y) in the grid
                    d_grid.push_back(std::make_pair(x, y));
                    //std::cout << x << y << '\n';
               
                } else {
                    // Print a warning for unsupported file formatting
                    std::cout << "Unsupported file formatting in world file" << '\n';
                }
            }
        }
    // File is automatically closed when 'file' goes out of scope
}

/**
 * @brief Determines the color of the tile at the specified coordinates.
 * 
 * This function checks if the given robot coordinates correspond to a colored tile
 * in the environment's grid and returns the color of the tile.
 * 
 * @param x The x-coordinate of the robot.
 * @param y The y-coordinate of the robot.
 * @return A boolean value representing the color of the tile (1 for white, 0 for black).
 */




int Environment::getSample(double x, double y, int method_read) {
    // Check if the robot coordinates correspond to a colored tile
    if (method_read ==0){
        for (std::pair<int, int> coloredTile : d_grid) {
            if (
                (x >= 1.0 * coloredTile.first / d_nrTiles) &&
                (x <= (1.0 * coloredTile.first + 1) / d_nrTiles) &&
                (y >= 1.0 * coloredTile.second / d_nrTiles) &&
                (y <= (1.0 * coloredTile.second + 1) / d_nrTiles)
            ) {

                // Print debug information if DEBUG is enabled
                return 1; // WHITE TILE
            }
        }

        // Print debug information if DEBUG is enabled

        return 0; // BLACK TILE
    }
    if (method_read ==1){
        
    }
}










#endif