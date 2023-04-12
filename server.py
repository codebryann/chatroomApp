import socket
import threading

host = ''
port = 18000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(1)

clients = []
usernames = []
chat_history = [] #need to implement this

#variables we need to implement 1 if true 0 is false
REPORT_REQUEST_FLAG = 0
REPORT_RESPONSE_FLAG = 0
JOIN_REQUEST_FLAG = 0
JOIN_REJECT_FLAG = 0
JOIN_ACCEPT_FLAG = 0
NEW_USER_FLAG = 0
QUIT_REQUEST_FLAG = 0
QUIT_ACCEPT_FLAG = 0
ATTACHMENT_FLAG = 0 # optional extra credit : If this message sends the contents of a file, this field is 1. Otherwise, it is 0.
NUMBER = 0 # If this is a report response message where REPORT_RESPONSE_FLAG=1, this field will be set to X, where X is the number of active users, which is in range [0-3]. Otherwise, it is 0.
USERNAME = "" # JOIN_REQUEST_FLAG=1 or JOIN_ACCEPT_FLAG=1 or NEW_USER_FLAG=1 or QUIT_ACCEPT_FLAG=1, this field is the username else its empty
FILENAME = "" # extra credit optional name of file being attached
PAYLOAD_LENGTH = 0 # length of message in characters
PAYLOAD = "" # contents of message


def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            broadcast(f"{username} has left the chat".encode())
            usernames.remove(username)
            break

def recieve():
    while True:
        client, address = server.accept()
        client.send("Welcome to the server!".encode())
        print(f"Connected to {address}")

        client.send("USER".encode())
        username = client.recv(1024).decode()
        usernames.append(username)
        clients.append(client)

        print(f"username of client is {username}!")
        broadcast(f"{username} has joined the chat!".encode())

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("Server is ready to recieve messages")
recieve()