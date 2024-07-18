
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <stdlib.h>

char *pPath = getenv("WB_WORKING_DIR");


class ControllerSettings
{
public:
    std::vector<double> values;
    void readSettings();
    
};


void ControllerSettings::readSettings()
{   
    char prob_name[256];
    sprintf(prob_name, "%s/c_settings.txt", pPath);

    //Dont set the parameters if the pointer is NULL
    if (pPath != NULL) {
        std::ifstream file(prob_name);
        std::string line;
        while (std::getline(file, line)){
            const char *cstr = line.c_str();
            values.push_back(atof(cstr));
   

        };
        file.close();
    }
    else{
        std::ifstream file("c_settings.txt");
        std::string line;
        while (std::getline(file, line)){
            const char *cstr = line.c_str();
            values.push_back(atof(cstr));

        };
        file.close();
    }

}

