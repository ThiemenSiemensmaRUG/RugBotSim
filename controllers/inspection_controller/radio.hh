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
    emitter->send(data, size);
}

/**
 * @brief Receives messages from the rover.
 *
 * @return std::vector<int> The received messages.
 */
std::vector<int> Radio_Rover::getMessages() {
    std::vector<int> messages;

    while (receiver->getQueueLength() > 0) {
        int temp = *(const int *)receiver->getData();
        messages.push_back(temp);

        receiver->nextPacket();
    }

    return messages;
}

#endif  // INCLUDED_MESSAGE_HANDLER_H_