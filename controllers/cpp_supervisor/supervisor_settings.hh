
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <stdlib.h>

char *pPath = getenv("WB_WORKING_DIR");


class SupervisorSettings
{
public:
    std::vector<double> values;
    void readSettings();
    SupervisorSettings();
    
};
SupervisorSettings::SupervisorSettings() {
    readSettings();
}

void SupervisorSettings::readSettings()
{   
    char prob_name[256];
    sprintf(prob_name, "%s/s_settings.txt", pPath);
    
    //Dont set the parameters if the pointer is NULL
    if (pPath != NULL) {
        std::ifstream file(prob_name);
        std::string line;
        while (std::getline(file, line)){
            const char *cstr = line.c_str();
            values.push_back(atof(cstr));
            //std::cout<<"setting = "<<cstr<<'\n';

        };
        file.close();
    }
    else{
        std::ifstream file("s_settings.txt");
        std::string line;
        while (std::getline(file, line)){
            const char *cstr = line.c_str();
            values.push_back(atof(cstr));
            //std::cout<<"setting = "<<cstr<<'\n';
        };
        file.close();
    }

}
