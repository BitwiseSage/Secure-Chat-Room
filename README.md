Secure Multi-Room Chat System with SSL & Performance Evaluation

Computer Networks Mini Project — Socket Programming

Overview

This project implements a secure multi-client chat system using TCP socket programming with SSL/TLS encryption. The system supports multiple chat rooms, private messaging, encrypted secret messaging, file transfer, along with performance evaluation, scalability testing, message ordering guarantees, and failure handling mechanisms.

The system demonstrates:

Concurrent client handling
Custom application-layer protocol design
Secure communication using SSL/TLS
Application-layer encryption (Fernet)
Message ordering guarantees
Scalability benchmarking
Latency measurement
Failure scenario handling
Features
Core Features (Deliverable 1)
Multi-client concurrent chat server
Multiple chat rooms
Private messaging between users
Encrypted secret messaging (Fernet)
File transfer between clients
SSL/TLS secured communication
Custom JSON-based protocol
Advanced Features (Deliverable 2)
Performance Evaluation & Scalability Testing

Implemented using:

load_test.py

Measures:

concurrent connection handling
connection success rate
connection time
server responsiveness under load
Message Ordering Guarantee per Room

Each message is assigned a sequence number:

MSG#1
MSG#2
MSG#3

Stored inside:

message_order_log.txt

Ensures ordered delivery within chat rooms.

Failure Scenario Handling

Server safely handles:

unexpected client disconnects
invalid packets
socket failures
interrupted file transfers

Disconnected clients are removed automatically without crashing the server.

Broadcast Latency Measurement

Server measures broadcast latency during message delivery.

Used for:

performance comparison
scalability evaluation
optimization validation
Optimization Techniques Implemented

Includes:

Thread-per-client architecture
Lock-based synchronization
Chunk-based file transfer
Broadcast exclusion optimization
Structured JSON communication protocol
Technologies Used
Python
TCP Socket Programming
SSL/TLS Encryption
Threading (Concurrency)
JSON Protocol Design
Cryptography (Fernet)
Project Architecture
Client
   │
   │ SSL Socket
   ▼
Server
   │
   ├── Room Manager
   ├── Message Ordering System
   ├── File Transfer Handler
   ├── Private Messaging Handler
   ├── Secret Encryption Layer
   └── Performance Logger
Running the Server

Start the server:

python server.py

Expected output:

Server running with SSL...
Connection from ('client_ip', port)
Running the Client

Start client:

python client.py

Enter:

username
room_name
Available Commands
Normal Room Message
hello everyone
Private Message
/private username message

Example:

/private Alice hello
Secret Encrypted Message
/secret username message

Example:

/secret Bob confidential text

Encrypted before transmission using Fernet symmetric encryption.

File Transfer
/file filename.txt

Example:

/file notes.txt

Received files stored inside:

received_files/
Performance Testing

Run scalability benchmark:

python load_test.py

Example output:

Clients requested: 20
Clients connected: 19
Connection success rate: 95%
Total connection time: 1.659 seconds
Message Ordering Log

Stored in:

message_order_log.txt

Example:

[ROOM room1] MSG#1 Alice: Hello
[ROOM room1] MSG#2 Bob: Hi

Ensures ordered delivery within rooms.

Failure Handling Demonstration

Server automatically handles:

unexpected disconnects
invalid packets
socket drops

Example server output:

username disconnected
Server Output Screenshots

Add screenshots here:

docs/server_output.png
docs/message_order_log.png
docs/file_transfer_server.png
docs/disconnect_handling.png
Client Output Screenshots

Add screenshots here:

docs/client_chat.png
docs/private_message.png
docs/secret_message.png
docs/file_receive.png
Performance Comparison Results

Add scalability comparison screenshots here:

docs/load_test_5_clients.png
docs/load_test_20_clients.png
docs/load_test_50_clients.png

Example comparison table:

Clients	Success Rate	Connection Time
5	XX%	X sec
10	XX%	X sec
20	XX%	X sec
50	XX%	X sec
Optimization Improvements Summary
Optimization	Purpose
Thread-per-client architecture	Enables concurrency
Lock-based synchronization	Prevents race conditions
Chunked file transfer	Efficient memory usage
Room-based broadcasting	Reduces unnecessary traffic
Sequence numbering	Ensures message ordering
Latency measurement	Enables performance evaluation
Project File Structure
server.py
client.py
protocol.py
encryption_utils.py
file_transfer.py
load_test.py
cert.pem
key.pem
message_order_log.txt
received_files/
README.md
Security Features Implemented

Layer 1:

SSL/TLS socket encryption

Layer 2:

Application-layer symmetric encryption (Fernet)

Protects:

room messages
private messages
secret messages
file transfer streams
Future Improvements

Possible extensions:

GUI client interface
persistent message storage
database-based authentication
UDP fast messaging mode
async server architecture
group-level encryption keys
Authors

Computer Networks Mini Project
Secure Multi-Room Chat System with Performance Evaluation and SSL Encryption