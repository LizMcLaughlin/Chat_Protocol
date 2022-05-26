# Chat Protocol

This protocol facilitates a chat session between two or more participants. It's designed for a client server paradigm where messages are passed from client to server, and forwarded onto the designated recipient(s). It promotes reliability and efficiency of message passing, while maintaining data integrity across differing machines and operating systems.

## Files

- client.py: client executable
- server.py: server executable
- design.pdf: protocol design documentation
- sample_run.pdf: sample run of program (terminal activity and GUI images)

## To Run Simulation

Please enter the below on the command line of two different terminal windows (Linux environment)
 
 ```sh
>> ./server.py
>> ./client.py
```

Client program will prompt for HOST and encoding specifications. Leave HOST blank ('enter' to proceed forward) for the purposes of this simulation. The below were entered as commanded for sample run in sample_run.pdf.

 ```sh
HOST: 
Encode format: utf8
```

Usernames and passwords for registered clients in form (username: pw):

- Liz: pw1
- Steve: pw2
- Bailey: pw3

## Analysis - Protocol Requirements Met

### Stateful

Both server and client program have a “delegate( )” function that manages state. It reads in methods (server), or response messages (client) and directs to the appropriate function representing the state of our DFA the client should be in. If the wrong method/response message is read in, it cannot move into the next state.
server.py:
def accept (server.py) -> “LISTEN” state
def authenticate (server.py) -> “USER AUTHENTICATION” state
def broadcast_new_connection (server.py) -> “PASS AUTHENTICATION” state def broadcast (server.py) -> “BROADCAST MSG” state
def quit (server.py) -> “LISTEN” state

### Concurrent

I decided to play with both threading and select in my implementation. My server uses the select module to enable multi client access. A selector object is created for the server to monitor for incoming connection requests. Then an additional selector is created for each client to listen for and direct incoming read events to the delegate function. As mentioned earlier, the delegate function directs the event to the appropriate function (state) after parsing the packet and reading in the method request.
Threading is used in the client program to allow for incoming messages concurrent with sending. A separate thread of control is created for messages appending to the chat window. The client can then type and send messages concurrently.

### Service

The server is bound to hardcoded port number 33318. The client program has this number hardcoded within.

### Client

The client can specify the the hostname or IP address when initiating the program. The client program is initiated by running the below on the command line:
$ ./client.py
The program then prompts for “Host”, enabling the client to specify hostname or IP address.
$ Host:

### UI

After the user enters host and prefered encoding information on the command line, all remaining activity is through the GUI interface. The user does not see any protocol logic while operating the chat app. Messages are sent and received through GUI windows and buttons.


Language: python3



