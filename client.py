import socket
import threading
import time

# optional, we can use tkinter to make gui for application

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

username = ""
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('', 18000))

flags = 00000000000000
def receive():
    while True:
        print("Choose an option (1, 2, or 3):")
        choice = input("1.Get a report of the chatroom from the server.\n2.Request to join the chatroom.\n3.Quit the program\n")

        if choice == "1":
            client.send("".encode, REPORT_REQUEST_FLAG)
        elif choice == "2":
            while True:
                try:
                    msg = client.recv(1024, flags)
                    if flags == NEW_USER_FLAG:
                        username = input("Enter a username: ")
                        client.send(username.encode())
                    elif flags == JOIN_ACCEPT_FLAG:
                        write_thread = threading.Thread(target=write(username))
                        write_thread.start()
                        connectedtochat = False
                    else:
                        print(msg.decode())
                except:
                    print("You have left the server.")
                    client.send("".encode, QUIT_REQUEST_FLAG)
                    client.close()
                    break

        elif choice == "3":
            print("Thank you for using our program!")
            client.send("".encode(), QUIT_REQUEST_FLAG)
            break
        else:
            print("Invalid choice")




    """"
    while True:
        try:
            msg = client.recv(1024, flags)
            if flags == NEW_USER_FLAG:
                username = input("Enter a unique username: ")
                client.send(username.encode())
            else:
                print(msg.decode())
        except:
            print("You have left the server.")
            client.send("".encode(), QUIT_REQUEST_FLAG)
            client.close()
            break"""

def write():
    PAYLOAD = ""
    while PAYLOAD != f"{username}: q":
        PAYLOAD = f"{username}: " + input(username+": ")
        if PAYLOAD != f"{username}: q":
            current_time = time.strftime("[%H:%M:%S] ")
            client.send((current_time+PAYLOAD).encode(), flags)
    client.send("".encode(), QUIT_REQUEST_FLAG)
    client.close()

receive_thread = threading.Thread(target = receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
