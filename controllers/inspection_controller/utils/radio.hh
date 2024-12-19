#ifndef INCLUDED_MESSAGE_HANDLER_H_
#define INCLUDED_MESSAGE_HANDLER_H_

#include <iterator>  // for ostream_iterator
#include <vector>
#include <webots/Emitter.hpp>
#include <webots/Receiver.hpp>
#include <webots/Supervisor.hpp>

using namespace webots;

class Radio_Rover {
    Emitter *emitter;
    Receiver *receiver;

   public:
    Radio_Rover() = default;
    Radio_Rover(Supervisor *robot, int d_);
    void sendMessage(const int *data, int size);
    std::vector<int> getMessages();
};

/**
 * @brief Construct a new Radio_Rover::Radio_Rover object
 *
 * @param robot
 * @param timeStep The time step of the simulation.
 */
Radio_Rover::Radio_Rover(Supervisor *robot, int timeStep) {
    emitter = robot->getEmitter("emitter");
    receiver = robot->getReceiver("receiver");
    receiver->enable(timeStep);
}   

/**
 * @brief Sends a message to the rover.
 *
 * @param data The data to be sent.
 * @param size The size of the data.
 */
void Radio_Rover::sendMessage(const int *data, int size) {
    // Print the entire array for debugging
    std::cout << "Sending data: ";
    for (int i = 0; i < ((size) / sizeof(int)); ++i) {
        std::cout << data[i] << " ";  // Print each integer in the array
    }
    std::cout << std::endl;

    // Send the data via the emitter
    emitter->send(data, size);
}

/**
 * @brief Receives messages from the rover.
 *
 * @return std::vector<int> The received messages.
 */


std::vector<int> Radio_Rover::getMessages() {
    std::vector<int> messages;

    // Iterate through all received packets
    while (receiver->getQueueLength() > 0) {
        // Get a pointer to the incoming data (interpreted as an array of integers)
        const int* data = static_cast<const int*>(receiver->getData());
        int dataSize = receiver->getDataSize() ;
        int numIntegers = dataSize / sizeof(int);  // Assuming sizeof(int) == 4 bytes

        // Assuming each packet consists of 3 integers (x, y, sample_value)
        for (int i = 0; i < numIntegers; ++i) {
            messages.push_back(data[i]); // Add each integer to the messages vector
        }

        // Move to the next packet in the receiver's queue
        receiver->nextPacket();
    }

    return messages;
}

#endif  // INCLUDED_MESSAGE_HANDLER_H_