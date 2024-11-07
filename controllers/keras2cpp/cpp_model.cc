#include "src/model.h"
#include <iostream>
#include <fstream>
#include <vector>

using keras2cpp::Model;
using keras2cpp::Tensor;

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: ./keras2cpp <input_file>" << std::endl;
        return 1;
    }

    // Load the model
    auto model = Model::load("cnn_model.model");

    // Open the input file
    std::ifstream infile(argv[1]);
    if (!infile.is_open()) {
        std::cerr << "Error: Unable to open file " << argv[1] << std::endl;
        return 1;
    }

    // Read values into a vector
    std::vector<double> values;
    double val;
    while (infile >> val) {
        values.push_back(val);
    }

    // Check that we have exactly 72 values
    if (values.size() != 72) {
        std::cerr << "Error: Expected 72 values for input data (24x3 matrix)." << std::endl;
        return 1;
    }

    // Create a tensor with shape (24, 3, 1) and fill it with values
    Tensor in{24, 3, 1};
    for (size_t i = 0; i < values.size(); ++i) {
        in.data_[i] = values[i];
    }

    // Run the model prediction
    Tensor out = model(in);

    // Print the output
    out.print();

    return 0;
}
