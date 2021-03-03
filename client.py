import socket, threading, sys, re, os.path, argparse, time
from shutil import copyfile

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cl = socket.gethostname()
SERVER_PORT = 7734
s.connect((cl, SERVER_PORT))
local_rfcs = []
# global done
# done = False

# Define the Argument Parser to get upload port,
# hostname, initial RFCs of the client
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--upload_port", help = "Client's upload port")
parser.add_argument("-host", "--hostname", help = "Client's hostname")
parser.add_argument("-r", "--rfcs", help = "Initial RFCs to start the client with", nargs="+")
args = parser.parse_args()


# Regex for extracting RFC number from request/response message
def getRFCNumber(msg):
    match = re.search(r'RFC\s(\d+)', msg)
    if match:
        return match.group(1)


# Regex for extracting protocol version from request/response message
def getProto(msg):
    return re.findall(r'P2P.*', msg)[0]


# Regex for extracting the hostname of client from request/response message
def getPeerName(msg):
    match = re.search(r'Host:\s?(.*)', msg)
    if match:
        return match.group(1)


# Regex for extracting the upload port of peer from response message to a GET request
def getPeerPort(msg):
    match = re.search(r'RFC.*?(\d+)$', msg)
    if match:
        return match.group(1)


# Generate LOOKUP request message of protocol
def generateLookupMsg(rfc_num):
    lookup_msg = 'LOOKUP RFC ' + rfc_num + " P2P-CI/1.0\n"
    lookup_msg += "Host: " + client_name + "\n"
    lookup_msg += "Port: " + str(s_port) + "\n"
    lookup_msg += "Title: Title of the RFC " + rfc_num
    return lookup_msg


# Generate LIST request message of protocol
def generateListMsg():
    list_msg = "LIST ALL P2P-CI/1.0\n"
    list_msg += "Host: " + client_name + "\n"
    list_msg += "Port: " + str(s_port) + "\n"
    return list_msg


# Generate CLOSE request message to signal server to delete client records
def generateCloseMsg():
    close_msg = "CLOSE P2P-CI/1.0\n"
    close_msg += "Host: " + client_name + "\n"
    return close_msg



def clientUpload():
    '''
    The upload port thread of this client points to the following 
    function to execute to listen for incoming GET requests from other peers
    '''
    
    sock.listen(5)
    # print('CLIENTUPLOAD')
    c, a = sock.accept()
    # print('ACCEPTED')
    req_msg = c.recv(16384).decode('utf-8')
    print(req_msg)
    print("\n")
    if 'GET' in req_msg:
        rfc_send = getRFCNumber(req_msg)
        path = "RFCs/rfc" + rfc_send + ".txt"
        with open(path, "r") as f:
            sendRFC = f.read(16384)
            # print(sendRFC)
            while sendRFC:
                c.send(bytes(sendRFC, 'utf-8'))
                sendRFC = f.read(16384)
    else:
        print("***Incorrect GET Request***")
    

# Binding a socket to the upload port of this client
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_port = int(args.upload_port)
host = socket.gethostname()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# print(host, str(s_port))
sock.bind((host, s_port))
cli_upload_thread = threading.Thread(target=clientUpload)
cli_upload_thread.start()

# Store the client_hostname and initial RFCs in variables
client_name = args.hostname
for i in args.rfcs:
    local_rfcs.append(i)
cwd = os.getcwd()
mkdir = os.path.join(cwd, client_name)
if not os.path.exists(mkdir):
    os.makedirs(mkdir)
for rfc in local_rfcs:
    copyfile("RFCs/rfc" + rfc + ".txt", client_name + "/" + rfc + ".txt")

# # Handling the Ctrl+C KeyboardInterrupt
# def signal_handler(signal, frame):
#     #print('You pressed Ctrl+C!')
#     sys.exit(0)
#     signal.signal(signal.SIGINT, signal_handler)
#     while 1:
#         continue
# def exitProgram():
#     done = True


def serverSend(req_msg):
    '''
        This function handles the sending and reception of messages
        related to LOOKUP, LIST and CLOSE protocol messages
    '''
    print('*'*50)
    s.send(bytes(req_msg, 'utf-8'))
    resp_msg = s.recv(16384).decode('utf-8')
    print(resp_msg)
    print("\n")
    # The following part is triggered automatically if a peer containing
    # the requested RFC is found.
    if 'LOOKUP' in req_msg and '200' in resp_msg:
        rfc_get = getRFCNumber(resp_msg)
        get_msg = 'GET RFC ' + rfc_get + " " + getProto(req_msg) + '\n'
        get_msg += 'Host: ' + getPeerName(req_msg) + '\n' + 'OS: MAC OS 10.4.1\n'
        req_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        req_port = getPeerPort(resp_msg)
        # print(req_port)
        req_host = socket.gethostname()
        req_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        req_sock.connect((req_host, int(req_port)))
        req_sock.send(bytes(get_msg, 'utf-8'))
        
        with open("./" + client_name + "/" + rfc_get + ".txt", "w+") as f:
            recvRFC = req_sock.recv(16384).decode('utf-8')
            # print(recvRFC)
            while recvRFC:
                f.write(recvRFC)
                recvRFC = req_sock.recv(16384).decode('utf-8')
        req_sock.close()
        local_rfcs.append(rfc_get)
        addRFC(rfc_get)

        # print(local_rfcs)
    if 'CLOSE' in req_msg and '200' in resp_msg:
        print("Leaving the P2P-CI system...\n")
        print("Connection closed.")
        # done = True
        # sys.exit()
        os._exit(1)
    

def addRFC(rfc):
    add_msg = "ADD RFC " + rfc + " P2P-CI/1.0\n"
    add_msg += "Host: " + client_name + "\n"
    add_msg += "Port: " + str(s_port) + "\n"
    add_msg += "Title: Title of the RFC " + rfc
    s.send(bytes(add_msg, 'utf-8'))
    resp_msg = s.recv(16384).decode('utf-8')
    print(resp_msg)
    print("\n")


def advertise():
    '''
        This function handles the initial advertisement of local RFCs
        to the server.
    '''
    for rfc in local_rfcs:
        add_msg = "ADD RFC " + rfc + " P2P-CI/1.0\n"
        add_msg += "Host: " + client_name + "\n"
        add_msg += "Port: " + str(s_port) + "\n"
        add_msg += "Title: Title of the RFC " + rfc
        s.send(bytes(add_msg, 'utf-8'))
        resp_msg = s.recv(16384).decode('utf-8')
        print(resp_msg)
        print("\n")


client_menu = {}
client_menu['1'] = 'Advertise to server'
client_menu['2'] = 'Lookup & Get RFC'
client_menu['3'] = 'List All RFCs'
client_menu['4'] = 'Leave P2P'

while True:
    for opt in sorted(client_menu):
        print(opt + ".\t\t" + client_menu[opt])
    choice = input("Please Choose: \n")
    print("\n")
    if choice == '2':
        RFC_to_get = input("Enter the RFC number of the RFC you wish to download: ")
        req_msg = generateLookupMsg(RFC_to_get)
    elif choice == '3':
        print('Here\'s the list of all the RFCs from the server:\n')
        req_msg = generateListMsg()
    elif choice =='4':
        req_msg = generateCloseMsg()

    if choice == '1':
        advertise_thread = threading.Thread(target= advertise)
        # advertise_thread.daemon = True
        advertise_thread.start()
    elif choice == '2' or choice == '3' or choice == '4':
        server_send_thread = threading.Thread(target= serverSend, args=(req_msg,))
        server_send_thread.start()
    time.sleep(2)

s.close()