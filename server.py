import socket
import threading

host = ''
port = 18000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(1)

clients = []
usernames = []
addresses = []
chat_history = [] #need to implement this

#FLAGS
REPORT_REQUEST_FLAG = 0b00000001 #client
REPORT_RESPONSE_FLAG = 0b00000010
JOIN_REQUEST_FLAG = 0b00000100 #client
JOIN_REJECT_FLAG = 0b00001000
JOIN_ACCEPT_FLAG = 0b00010000
NEW_USER_FLAG = 0b00100000
QUIT_REQUEST_FLAG = 0b01000000#client
QUIT_ACCEPT_FLAG = 0b10000000
ATTACHMENT_FLAG = 0  #optional extra credit : If this message sends the contents of a file, this field is 1. Otherwise, it is 0.
NUMBER = 0  #If this is a report response message where REPORT_RESPONSE_FLAG=1, this field will be set to X, where X is the number of active users, which is in range [0-3]. Otherwise, it is 0.
USERNAME = ""  #JOIN_REQUEST_FLAG=1 or JOIN_ACCEPT_FLAG=1 or NEW_USER_FLAG=1 or QUIT_ACCEPT_FLAG=1, this field is the username else its empty
FILENAME = ""  #extra credit optional name of file being attached
PAYLOAD_LENGTH = 0  #length of message in characters
PAYLOAD = ""  #contents of message

flags = 0b00000000000000

def broadcast(PAYLOAD):
    for client in clients:
        client.send(PAYLOAD)
    chat_history.append(PAYLOAD)

def handle(client):
    while True:
        try:
            PAYLOAD = client.recv(1024)
            broadcast(PAYLOAD)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            address = addresses[index]
            addresses.remove(address)
            broadcast(f"{username} has left the chat".encode())
            usernames.remove(username)
            break

def recieve():
    while True:
        client, address = server.accept()
        request = client.recv(1024, flags)
        if flags is REPORT_REQUEST_FLAG:
            NUMBER = len(usernames)
            PAYLOAD = ""
            if NUMBER != 0:
                for i in range(0,NUMBER):
                    PAYLOAD += str(i)+ f"{usernames[i]} at {clients[i]} and port {addresses[i]}\n"
            client.send(PAYLOAD.encode(), REPORT_RESPONSE_FLAG)
        elif flags is JOIN_REQUEST_FLAG:
            if len(usernames) < 3:
                while True:
                    client.send("".endcode(), NEW_USER_FLAG)
                    USERNAME = client.recv(1024).decode()
                    if USERNAME in usernames:
                        continue
                    else:
                        client.send("Welcome to the Chatroom!".encode(), JOIN_ACCEPT_FLAG)
                        print(f"Connected to {address}")
                        usernames.append(USERNAME)
                        clients.append(client)
                        addresses.append(address)
                        for message in chat_history: #might move into handle before while true
                            client.send(message)
                        print(f"username of client is {USERNAME}!")
                        broadcast(f"{USERNAME} has joined the chat!".encode())
                        thread = threading.Thread(target=handle, args=(client,))
                        thread.start()
            else:
                client.send("Chatroom is Full".encode(), JOIN_REJECT_FLAG)
        elif flags is QUIT_REQUEST_FLAG:
            index = clients.index(client)
            client.send("".encode(), QUIT_ACCEPT_FLAG)
            clients.remove(client)
            client.close()
            USERNAME = usernames[index]
            broadcast(f"{USERNAME} has left the chat".encode())
            usernames.remove(USERNAME)
            address = address[index]
            addresses.remove(address)
        PAYLOAD_LENGTH = len(PAYLOAD.decode())



print("Server is ready to recieve messages")
recieve()