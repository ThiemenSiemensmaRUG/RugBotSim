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
        enum class Method {
        Modal = 1,
        Vibration = 2,
        // Add more methods of reading data as needed
    };
    double lastSample = 0.0;

    Sampling() {};

    void setMethod(int methodNumber) ;

    void initializer(int isDamaged, int modeNumber, int methodRead);
    // Function to initialize the file path based on the 'isDamaged' argument
    void initialize_paths(int isDamaged);
    // Function to read the node mappings and store them in a vector
    void read_node_mappings();
    //read modal shape data
    void read_modal_shape_data(int ModeNumber);
    // build lookup map
    void build_mode_shape_map();

    double find_u3_by_label(int label);
    std::vector<FEM_Node> get_interpolation_nodes(int px, int py);
    double getModalData(int posx, int posy);
    double getVibrationData(int posx, int posy);
    double getSample(int posx, int posy);

    bool pos_in_between_nodes(int posx, int posy, std::vector<FEM_Node> nodes);
    
    private:
        Method selectedMethod;

        std::unordered_map<int, double> modeShapeMap; // Optimized lookup map for finding u3 based on label
        std::string mappingPath;
        std::string modalPath;
        std::string vibrationPath;
        std::vector<FEM_Node> nodes; // Vector to store the node mappings
        std::vector<ModeShape> modeShapes; //vector to store readings of mode shape 
};

void Sampling::initializer(int isDamaged, int modeNumber, int methodRead){
    initialize_paths(isDamaged);
    read_node_mappings();
    read_modal_shape_data(modeNumber);
    build_mode_shape_map();
    setMethod(methodRead);

};

void Sampling::setMethod(int methodNumber) {
    switch (methodNumber) {
        case 1:
            selectedMethod = Method::Modal;
            std::cout << "Method set to: Modal direct" << std::endl;  // Print which method is set
            break;
        case 2:
            selectedMethod = Method::Vibration;
            std::cout << "Method set to: Vibration" << std::endl;  // Print which method is set
            break;
        default:
            std::cerr << "Invalid method number! Defaulting to Modal." << std::endl;
            selectedMethod = Method::Modal;
            std::cout << "Method set to: Modal (default due to invalid input)" << std::endl;  // Print default method
            break;
    }
}

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

void Sampling::build_mode_shape_map() {
    modeShapeMap.clear(); // Clear any existing data
    for (const auto& shape : modeShapes) {
        modeShapeMap[shape.label_num] = shape.u3;
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

    // Get the 3 closest nodes (if available)
    std::vector<FEM_Node> closestNodes;
    for (int i = 0; i < 3 && i < distances.size(); ++i) {  // Fixed the loop to include up to 3 nodes
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
    file.close();

}


double Sampling::find_u3_by_label(int label) {
    auto it = modeShapeMap.find(label); // Fast lookup in hash table
    if (it != modeShapeMap.end()) {
        return it->second; // Return the u3 value if found
    } else {
        std::cerr << "Label not found!" << std::endl;
        return -1.0; // Error case
    }
}

bool Sampling::pos_in_between_nodes(int posx, int posy, std::vector<FEM_Node> nodes) {
    if (nodes.size() != 3) {
        std::cerr << "Error: Exactly 3 nodes are required to form a triangle." << std::endl;
        return false;
    }

    // Extract vertices of the triangle
    const FEM_Node& A = nodes[0];
    const FEM_Node& B = nodes[1];
    const FEM_Node& C = nodes[2];

    // Calculate vectors
    double v0x = C.x - A.x;
    double v0y = C.y - A.y;
    double v1x = B.x - A.x;
    double v1y = B.y - A.y;
    double v2x = posx - A.x;
    double v2y = posy - A.y;

    // Calculate dot products
    double dot00 = v0x * v0x + v0y * v0y;
    double dot01 = v0x * v1x + v0y * v1y;
    double dot02 = v0x * v2x + v0y * v2y;
    double dot11 = v1x * v1x + v1y * v1y;
    double dot12 = v1x * v2x + v1y * v2y;

    // Compute barycentric coordinates
    double denom = dot00 * dot11 - dot01 * dot01;
    if (denom == 0.0) {
        std::cerr << "Error: Degenerate triangle." << std::endl;
        return false; // Degenerate triangle
    }

    double invDenom = 1.0 / denom;
    double u = (dot11 * dot02 - dot01 * dot12) * invDenom;
    double v = (dot00 * dot12 - dot01 * dot02) * invDenom;

    // Check if point is inside the triangle
    return (u >= 0) && (v >= 0) && (u + v <= 1);
}

double Sampling::getModalData(int posx, int posy){
    // Get the closest nodes around the point (posx, posy)
    std::vector<FEM_Node> closestNodes = get_interpolation_nodes(posx, posy);
    bool valid = pos_in_between_nodes(posx, posy, closestNodes);
    

    // Ensure we have exactly 3 nodes (forming a triangle)
    if ((closestNodes.size() != 3) || (!valid)) {
        std::cerr << "Error in computing sample" << std::endl;
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
    
    double u31 = find_u3_by_label(A.label_num);
    double u32 = find_u3_by_label(B.label_num);
    double u33 = find_u3_by_label(C.label_num);
    
    // Use distances as weights (inverse distance weighting)
    double weightA = 1.0 / distA;
    double weightB = 1.0 / distB;
    double weightC = 1.0 / distC;
    double totalWeight = weightA + weightB + weightC;

    // Weighted average of u3 values
    double weightedU3 = (weightA * u31 + weightB * u32 + weightC * u33) / totalWeight;
    lastSample = weightedU3;
    return weightedU3;
}

double Sampling::getVibrationData(int posx, int posy){
    return 30.4;
}

double Sampling::getSample(int posx, int posy){
    switch (selectedMethod) {
        case Method::Modal:
            return getModalData(posx, posy);
        case Method::Vibration:
            return getVibrationData(posx, posy);
        // Add more cases as needed
        default:
            std::cerr << "Unknown method selected!" << std::endl;
            return -1.0;
    }
}

#endif  // INCLUDED_SAMPLING_HH_