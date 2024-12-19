
#include <stdlib.h>

#include <fstream>
#include <iostream>
#include <string>
#include <vector>

char *pPath = getenv("WB_WORKING_DIR");

class ControllerSettings {
   public:
    std::vector<double> values;
    void readSettings();
};

void ControllerSettings::readSettings() {
    char prob_name[256];
    sprintf(prob_name, "%s/c_settings.txt", pPath);

    // Dont set the parameters if the pointer is NULL
    if (pPath != NULL) {
        std::ifstream file(prob_name);
        std::string line;
        while (std::getline(file, line)) {
            const char *cstr = line.c_str();
            values.push_back(atof(cstr));
            std::cout << "setting = " << cstr << '\n';
        };
        file.close();
    } else {
        std::ifstream file("c_settings.txt");
        std::string line;
        while (std::getline(file, line)) {
            const char *cstr = line.c_str();
            values.push_back(atof(cstr));
            std::cout << "setting = " << cstr << '\n';
        };
        file.close();
    }
}
