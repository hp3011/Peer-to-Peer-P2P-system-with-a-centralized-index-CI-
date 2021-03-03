# Peer-to-Peer-P2P-system-with-a-centralized-index-CI-

### Objective:
- becoming familiar with network programming and the socket interface
- creating server processes that wait for connections
- creating client processes that contact a well-known server and exchange data over the Internet
- defining a simple application protocol and making sure that peers and server follow precisely the
specifications for their side of the protocol in order to accomplish particular tasks
- creating and managing a centralized index at the server based on information provided by the peers, and
- implementing a concurrent server that is capable of carrying out communication with multiple clients
simultaneously.

The folder 'RFCs' contains a few of the hundreds of RFCs this project was tested with.

NOTE: The code is structured around the naming of the 'RFCs' folder and the actual RFC files inside it
      and hence, the 'RFCs' folder should be in the same directory as the Python scripts.
      The RFCs provided in the folder range from 8595 - 8605, 8695 - 8705, 8795 - 8805 (33 in total).
      Example of naming of the RFCs - For RFC 8600, the file name is rfc8600.txt


### Steps to run the P2P-CI system:
    1. Run the 'server.py' file with the command:
        python server.py
    
    2. Run the 'client.py' file:
        To get help about the arguments needed by the file:
            python client.py -h
        To run a client with parameters:
        (example)
            python client.py -p 2222 -host csc573.csc.ncsu.edu -r 8600 8601 8602
	When a client is run with the above command, the RFCs initiated are copied from the 'RFCs' folder
	to a new folder which is named as the value given to the 'host' argument in the command.
	Choose choice number 1 to advertise all Local RFCs in the beginning to the Server.
    
    3. Run multiple clients with the command shown in Step 2.
    4. The client menu has various operations:
        i. Advertise  - Initial ADD messages to the server to advertise RFCs
       ii. Lookup     - Lookup a specific RFC number and download it from one of the parameters
      iii. List       - List All RFCs registered with the CI on the Server
       iv. Close      - Close the connection with the server and exit the client program

	The corresponding request and response messages are printed at the Server and the Client 
	respectively.





The help of the 'client.py' file is given below (which can also be displayed using 'python client.py -h' -
	
**usage:** client.py [-h] [-p UPLOAD_PORT] [-host HOSTNAME] [-r RFCS [RFCS ...]]

**optional arguments:**
  -h, --help            show this help message and exit
  -p UPLOAD_PORT, --upload_port UPLOAD_PORT
                        Client's upload port
  -host HOSTNAME, --hostname HOSTNAME
                        Client's hostname
  -r RFCS [RFCS ...], --rfcs RFCS [RFCS ...]
                        Initial RFCs to start the client with

