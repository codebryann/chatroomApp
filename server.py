import socket
import threading

host = ''
port = 18000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(1)

clients = []
usernames = []

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