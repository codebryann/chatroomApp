import socket
import threading


username = input("Enter a username: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('', 18000))


def receive():
    while True:
        try:
            msg = client.recv(1024).decode()
            if msg == "USER":
                client.send(username.encode())
            else:
                print(msg)
        except:
            print("You have left the server.")
            client.close()
            break

def write():
    bmsg = ""
    while bmsg != f"{username}: q":
        msg = input("")
        bmsg = f"{username}: {msg}"
        if bmsg != f"{username}: q":
            client.send(bmsg.encode())
    client.close()

receive_thread = threading.Thread(target = receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
