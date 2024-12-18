#ifndef INCLUDED_SAMPLING_HH_
#define INCLUDED_SAMPLING_HH_

#include <filesystem>
#include <fstream>
#include <iostream>
#include <vector>

// Define a structure to represent each node with x and y pos and label
struct FEM_Node {
    int x;
    int y;
    int label_num;

    // Calculate the Euclidean distance between this node and another point (px, py)
    double distance(int px, int py) const {
        return std::sqrt(std::pow(x - px, 2) + std::pow(y - py, 2));
    }
};


struct ModeShape {
    double u3;
    int label_num;
};

class Sampling {
    public:
    double lastSample = 0.0;

    Sampling() {};
    void initializer(int isDamaged, int modeNumber);
    // Function to initialize the file path based on the 'isDamaged' argument
    void initialize_paths(int isDamaged);
    // Function to read the node mappings and store them in a vector
    void read_node_mappings();
    //read modal shape data
    void read_modal_shape_data(int ModeNumber);


    double find_u3_by_label(int label);
    std::vector<FEM_Node> get_interpolation_nodes(int px, int py);
    double getSample(int posx, int posy);

    
    private:
        
        std::string mappingPath;
        std::string modalPath;
        std::string vibrationPath;
        std::vector<FEM_Node> nodes; // Vector to store the node mappings
        std::vector<ModeShape> modeShapes; //vector to store readings of mode shape 
};

void Sampling::initializer(int isDamaged, int modeNumber){
    initialize_paths(isDamaged);
    read_node_mappings();
    read_modal_shape_data(modeNumber);

};

//iinitlize the paths to read the mode shapes and mode mapping
void Sampling::initialize_paths(int isDamaged) {
    std::filesystem::path currentPath = std::filesystem::current_path();
    std::filesystem::path basePath = currentPath.parent_path().parent_path();

    if (isDamaged == 1) {
        // If 1, set the path to the "damaged" folder
        mappingPath = (basePath / "measurements" / "damaged" / "_label_mapping.csv").string();
        modalPath = (basePath / "measurements" / "damaged" / "modal_shape.csv").string();
    } else {
        // If 0, set the path to the "undamaged" folder
        mappingPath = (basePath / "measurements" / "undamaged" / "_label_mapping.csv").string();
        modalPath = (basePath / "measurements" / "undamaged" / "modal_shape.csv").string();
    }
}


void Sampling::read_node_mappings() {
    nodes.clear();
    std::ifstream inputFile(mappingPath);
    if (!inputFile.is_open()) {
        std::cerr << "Failed to open file: " << mappingPath << std::endl;
        return;
    }

    std::string line;
    // Skip the header if present
    std::getline(inputFile, line);

    while (std::getline(inputFile, line)) {
        std::stringstream ss(line);
        std::string token;
        FEM_Node node;

        // Extract the values for x, y, and label_num from the CSV line
        std::getline(ss, token, ',');  // Get x value
        node.x = std::stoi(token);

        std::getline(ss, token, ',');  // Get y value
        node.y = std::stoi(token);

        std::getline(ss, token, ',');  // Get label_num value
        node.label_num = std::stoi(token);

        // Push the node to the vector
        nodes.push_back(node);
    }

    if (nodes.empty()) {
        std::cerr << "No nodes found in file: " << mappingPath << std::endl;
    } else {
        std::cout << "Successfully read " << nodes.size() << " nodes from the file." << std::endl;
    }
}

std::vector<FEM_Node> Sampling::get_interpolation_nodes(int px, int py) {
    // Create a vector to hold pairs of nodes and their distance to (px, py)
    std::vector<std::pair<double, FEM_Node>> distances;

    // Calculate distance for each node and store it with the corresponding node
    for (const auto& node : nodes) {
        double dist = node.distance(px, py);
        distances.push_back({dist, node});
    }

    // Sort the distances vector by distance (ascending order)
    std::sort(distances.begin(), distances.end(),
              [](const std::pair<double, FEM_Node>& a, const std::pair<double, FEM_Node>& b) {
                  return a.first < b.first;
              });

    // Get the 4 closest nodes (if available)
    std::vector<FEM_Node> closestNodes;
    for (int i = 0; i < 3 && i < distances.size(); ++i) {  // Fixed the loop to include up to 4 nodes
        closestNodes.push_back(distances[i].second);
    }

    return closestNodes;
}


void Sampling::read_modal_shape_data(int ModeNumber) {
    // Open the file
    modeShapes.clear();
    std::ifstream file(modalPath);
    if (!file.is_open()) {
        std::cerr << "Error opening file: " << modalPath << std::endl;
        return;
    }
    // Read the header line (assuming the file has a header row)
    std::string line;
    std::getline(file, line);  // Read header

    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string token;

        int label_num = 0, mode_num = 0; //, x = 0, y = 0;
        double u3 = 0.0;

        // Read fields from the CSV file, all using std::stod, and cast as needed
        std::getline(ss, token, ',');  // label_num
        label_num = static_cast<int>(std::stod(token));  // Convert to double first, then cast to int

        std::getline(ss, token, ',');  // x
        //x = static_cast<int>(std::stod(token));  // Convert to double first, then cast to int

        std::getline(ss, token, ',');  // y
        //y = static_cast<int>(std::stod(token));  // Convert to double first, then cast to int

        std::getline(ss, token, ',');  // z (skip)

        std::getline(ss, token, ',');  // mode_num
        mode_num = static_cast<int>(std::stod(token));  // Convert to double first, then cast to int

        std::getline(ss, token, ',');  // u1 (skip)
        std::getline(ss, token, ',');  // u2 (skip)

        std::getline(ss, token, ',');  // u3
        u3 = std::stod(token);  // Keep as double

        // Check if this row's mode_num matches the input ModeNumber
        if (mode_num == ModeNumber) {
            // Store the result in the modeShapes vector
            ModeShape shape;
            shape.u3 = u3;
            shape.label_num = label_num;
            modeShapes.push_back(shape);
        }
    }

    // Close the file
    file.close();

    // Optional: Print out the filtered results
    std::cout << "Filtered data for ModeNumber " << ModeNumber << ":\n";
    // for (const auto& shape : modeShapes) {
    //     std::cout << "u3: " << shape.u3 << ", label_num: " << shape.label_num << std::endl;
    // }
}


double Sampling::find_u3_by_label(int label) {
    // Use std::find_if to find the first ModeShape with the given label
    auto it = std::find_if(modeShapes.begin(), modeShapes.end(), [label](const ModeShape& shape) {
        return shape.label_num == label;
    });

    // If found, return the u3 value, otherwise return an error value (e.g., -1)
    if (it != modeShapes.end()) {
        return it->u3;
    } else {
        std::cerr << "Label not found!" << std::endl;
        return -1.0;  // Error case
    }
}


double Sampling::getSample(int posx, int posy){
// Get the closest nodes around the point (posx, posy)
    std::vector<FEM_Node> closestNodes = get_interpolation_nodes(posx, posy);

    // Ensure we have exactly 3 nodes (forming a triangle)
    if (closestNodes.size() != 3) {
        std::cerr << "Error: Not enough nodes to compute sample." << std::endl;
        return 0.0;
    }
        // Get the 3 closest nodes
    FEM_Node A = closestNodes[0];
    FEM_Node B = closestNodes[1];
    FEM_Node C = closestNodes[2];
    // Calculate distances from the point (posx, posy) to each of the nodes
    double distA = A.distance(posx, posy);
    double distB = B.distance(posx, posy);
    double distC = C.distance(posx, posy);
    // Use distances as weights (inverse distance weighting)
    double weightA = 1.0 / distA;
    double weightB = 1.0 / distB;
    double weightC = 1.0 / distC;
    double totalWeight = weightA + weightB + weightC;

    double u31 = find_u3_by_label(A.label_num);
    double u32 = find_u3_by_label(B.label_num);
    double u33 = find_u3_by_label(C.label_num);

    // Weighted average of u3 values
    double weightedU3 = (weightA * u31 + weightB * u32 + weightC * u33) / totalWeight;
    lastSample = weightedU3;
    return weightedU3;
}


#endif  // INCLUDED_SAMPLING_HH_