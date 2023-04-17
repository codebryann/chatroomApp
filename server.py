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
REPORT_REQUEST_FLAG = "00000001" #client
REPORT_RESPONSE_FLAG = "00000010"
JOIN_REQUEST_FLAG = "00000100" #client
JOIN_REJECT_FLAG = "00001000"
JOIN_ACCEPT_FLAG = "00010000"
NEW_USER_FLAG = "00100000"
QUIT_REQUEST_FLAG = "01000000"#client
QUIT_ACCEPT_FLAG = "10000000"
ATTACHMENT_FLAG = 0  #optional extra credit : If this message sends the contents of a file, this field is 1. Otherwise, it is 0.
NUMBER = 0  #If this is a report response message where REPORT_RESPONSE_FLAG=1, this field will be set to X, where X is the number of active users, which is in range [0-3]. Otherwise, it is 0.
USERNAME = ""  #JOIN_REQUEST_FLAG=1 or JOIN_ACCEPT_FLAG=1 or NEW_USER_FLAG=1 or QUIT_ACCEPT_FLAG=1, this field is the username else its empty
FILENAME = ""  #extra credit optional name of file being attached
PAYLOAD_LENGTH = 0  #length of message in characters
PAYLOAD = ""  #contents of message

flags = "00000000"

def broadcast(PAYLOAD):
    if(PAYLOAD.decode() == QUIT_REQUEST_FLAG):
        pass
    else:
        for client in clients:
            client.send(PAYLOAD)
        chat_history.append((PAYLOAD.decode()+"\n").encode())

def handle(client):
    while True:
        try:
            PAYLOAD = client.recv(1024)
            if(PAYLOAD.decode() == QUIT_REQUEST_FLAG):
                print("quit request received")
                client.send(QUIT_ACCEPT_FLAG.encode())
                break
            else:
                PAYLOAD_LENGTH = len(PAYLOAD.decode())
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
    index = clients.index(client)
    clients.remove(client)
    client.close()
    username = usernames[index]
    address = addresses[index]
    addresses.remove(address)
    broadcast(f"{username} has left the chat".encode())
    usernames.remove(username)

def recieve(client, address):
    print("new thread")
    run = True
    while run:
        request = client.recv(1024)
        print("request recieved")
        if request.decode() == REPORT_REQUEST_FLAG:
            print("report request received")
            client.send(REPORT_RESPONSE_FLAG.encode())
            NUMBER = len(usernames)
            print(NUMBER)
            PAYLOAD = ""
            if NUMBER > 0:
                for i in range(0,NUMBER):
                    PAYLOAD += f"{str(i)}. {usernames[i]} at {addresses[i][0]} and port {addresses[i][1]}\n"
                client.send(PAYLOAD.encode())
            else:
                client.send("Chatroom is empty".encode())
        elif request.decode() == JOIN_REQUEST_FLAG:
            print("join request")
            if len(usernames) < 3:
                while True:
                    client.send(NEW_USER_FLAG.encode())
                    USERNAME = client.recv(1024).decode()
                    if USERNAME in usernames:
                        continue
                    else:
                        client.send(JOIN_ACCEPT_FLAG.encode())
                        print(f"Connected to {address}")
                        usernames.append(USERNAME)
                        clients.append(client)
                        addresses.append(address)
                        if len(chat_history) != 0:
                            for message in chat_history: #might move into handle before while true
                                client.send(message)
                        broadcast(f"{USERNAME} has joined the chat!".encode())
                        client.send("\nWelcome to the Chatroom!".encode())
                        thread = threading.Thread(target=handle, args=(client,))
                        thread.start()
                        run = False
                        break
            else:
                client.send(JOIN_REJECT_FLAG.encode())
        elif request.decode() == QUIT_REQUEST_FLAG:
            print("quit request accepted")
            client.send(QUIT_ACCEPT_FLAG.encode())
            client.close()
            run = False



def startup():
    while True:
        client, address = server.accept()
        print(f"connected to {address[0]} at port {address[1]}")
        thread = threading.Thread(target=recieve, args=(client, address))
        thread.start()




print("Server is ready to recieve messages")
startup()
