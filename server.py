import socket, threading, re, sys, signal

print('\nWelcome To The P2P-CI Sytem\n')
print('Server now running at Port 7734\n')
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 7734
host = socket.gethostname()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# print(host)
sock.bind((host, port))
sock.listen(5)

# List of tuples that stores RFC information -
# number, title, peer_name, peer's upload_port
rfc_info = []

# List of tuples storing Peer information -
# peer_hostname, peer's upload_port
peers = []


# def signal_handler(signal, frame):
#     print('You pressed Ctrl+C!')
#     sys.exit(0)
#     signal.signal(signal.SIGINT, signal_handler)
#     while 1:
#         continue

# Regex for extracting RFC number from a request message
def getRFCNumber(msg):
    match = re.search(r'RFC\s(\d+)', msg)
    if match:
        return match.group(1)


# Regex for extracting the hostname of client from a request message
def getPeerName(msg):
    match = re.search(r'Host:\s?(.*)', msg)
    if match:
        return match.group(1)


# Regex for extracting the upload port of client from a request message
def getPortNumber(msg):
    match = re.search(r'Port:\s?(.*)', msg)
    if match:
        return match.group(1)


# Regex for extracting the RFC title from an ADD request message
def getRFCTitle(msg):
    match = re.search(r'Title:\s?(.*)', msg)
    if match:
        return match.group(1)


# Regex for extracting the protocol version from a request message
def getProto(msg):
    return re.findall(r'P2P.*', msg)[0]


def remove_data(cli_name):
    '''
        Remove peer and RFC records of a client
        that wishes to leave the P2P-CI system
    '''
    
    global peers, rfc_info
    peers = [i for i in peers if not i[0] == cli_name]
    rfc_info = [i for i in rfc_info if not i[2] == cli_name]
    # print("*"*25)
    # print(peers)
    # print(rfc_info)


def createConnection(c, a):
    '''
        Handle 2-way communication with a client including error codes handling
    '''

    global peers, rfc_info
    # c.send(bytes("yolo", 'utf-8'))
    # print(c, a)
    print('*'*50)
    while True:
        req_msg = c.recv(16384).decode('utf-8')
        print(req_msg)
        print("\n")
        if 'ADD' in req_msg:
            if 'P2P-CI/1.0' not in req_msg:
                print('\n*****505 P2P-CI Version Not Supported*****\n')
            else:
                newRFC = (int(getRFCNumber(req_msg)), getRFCTitle(req_msg), getPeerName(req_msg), getPortNumber(req_msg))
                rfc_info.append(newRFC)
                cli_name = getPeerName(req_msg)
                if not any(cli_name in i for i in peers):
                    peers.append((cli_name, getPortNumber(req_msg)))
                    print(peers)
                    print("\n")
                # print(rfc_info)
                resp_msg = getProto(req_msg) + ' 200 OK\nRFC '
                resp_msg += ' '.join(str(i) for i in newRFC)
        elif 'LOOKUP' in req_msg:
            if 'P2P-CI/1.0' not in req_msg:
                print('\n*****505 P2P-CI Version Not Supported*****\n')
            else: 
                resp_peers = ''
                rfc_to_find = int(getRFCNumber(req_msg))
                for rfc in rfc_info:
                    if rfc_to_find == rfc[0]:
                        resp_peers = resp_peers + 'RFC ' + ' '.join(str(i) for i in rfc) + '\n'
                if resp_peers:
                    resp_msg = getProto(req_msg) + ' 200 OK\n' + resp_peers
                else:
                    resp_msg = getProto(req_msg) + ' 404 Not Found\n'
        elif 'LIST' in req_msg:
            if 'P2P-CI/1.0' not in req_msg:
                print('\n*****505 P2P-CI Version Not Supported*****\n')
            else:
                resp_peers = ''
                # print(rfc_info)
                for rfc in rfc_info:
                    resp_peers = resp_peers + 'RFC ' + ' '.join(str(i) for i in rfc) + '\n'
                if resp_peers:
                    resp_msg = getProto(req_msg) + ' 200 OK\n' + resp_peers
                else:
                    resp_msg = getProto(req_msg) + ' 404 Not Found\n'
        elif 'CLOSE' in req_msg:
            if 'P2P-CI/1.0' not in req_msg:
                print('\n*****505 P2P-CI Version Not Supported*****\n')
            else:
                # print("YOLO")
                cli_name = getPeerName(req_msg)
                remove_data(cli_name)
                resp_msg = getProto(req_msg) + ' 200 OK\n'
        else:
            print('\n*****P2P-CI/1.0 400 Bad Request*****\n')

        c.send(bytes(resp_msg, 'utf-8'))
        if 'CLOSE' in req_msg:
            c.close()
            break

    # c.close()



# Actively listen for connections from clients
while True:
    c, a = sock.accept()
    new_client_thread = threading.Thread(target=createConnection, args=(c, a,))
    new_client_thread.start()
    # print(c, a)
    # print(new_client_thread)
    # c.send(bytes("yolo", 'utf-8'))
    


sock.close()