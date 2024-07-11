#ifndef INCLUDED_MESSAGE_HANDLER_H_
#define INCLUDED_MESSAGE_HANDLER_H_

#include <vector>
#include <webots/Emitter.hpp>
#include <webots/Receiver.hpp>
#include <webots/Supervisor.hpp>
#include <iterator> // for ostream_iterator


using namespace webots;





class Radio_Rover
{
    Emitter *emitter;
    Receiver *receiver;

    public:
        Radio_Rover() = default;
        Radio_Rover(Supervisor *robot, int d_);
        void sendMessage(const int *data, int size);
        std::vector<int> getMessages();
};

Radio_Rover::Radio_Rover(Supervisor *robot, int timeStep)
{
    emitter = robot->getEmitter("emitter");
    receiver = robot->getReceiver("receiver");
    receiver->enable(timeStep);
   
}

void Radio_Rover::sendMessage(const int *data, int size)
{
   
    emitter->send(data, size);
    
    
}

std::vector<int> Radio_Rover::getMessages()
{
    std::vector<int> messages;
    
    while (receiver->getQueueLength() > 0) 
    {
        int temp = *(const int*) receiver->getData();
        messages.push_back(temp);   

        
        receiver->nextPacket();
    }
   
    return messages;
}

#endif