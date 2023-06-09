import socket
import threading
import time
import os,sys

# optional, we can use tkinter to make gui for application

#FLAGS
REPORT_REQUEST_FLAG = "00000001" #client
REPORT_RESPONSE_FLAG = "00000010"
JOIN_REQUEST_FLAG = "00000100" #client
JOIN_REJECT_FLAG = "00001000"
JOIN_ACCEPT_FLAG = "00010000"
NEW_USER_FLAG = "00100000"
QUIT_REQUEST_FLAG = "01000000"#client
QUIT_ACCEPT_FLAG = "10000000"
ATTACHMENT_FLAG = "100000000"  #optional extra credit : If this message sends the contents of a file, this field is 1. Otherwise, it is 0.
NUMBER = 0  #If this is a report response message where REPORT_RESPONSE_FLAG=1, this field will be set to X, where X is the number of active users, which is in range [0-3]. Otherwise, it is 0.
USERNAME = ""  #JOIN_REQUEST_FLAG=1 or JOIN_ACCEPT_FLAG=1 or NEW_USER_FLAG=1 or QUIT_ACCEPT_FLAG=1, this field is the username else its empty
FILENAME = ""  #extra credit optional name of file being attached
PAYLOAD_LENGTH = 0  #length of message in characters
PAYLOAD = ""  #contents of message

flags = "00000000"


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('', 18000))

def main():
    run = True
    while run:
        print("Choose an option")
        choice = input("1.Get a report of the chatroom from the server.\n2.Request to join the chatroom.\n3.Quit the program\n:")
        if choice == "1":
            time.sleep(.1)
            client.send(REPORT_REQUEST_FLAG.encode())
            response = client.recv(1024)
            if(response.decode() == REPORT_RESPONSE_FLAG):
                report = client.recv(1024)
                print(report.decode())
        elif choice == "2":
            taken = 0
            run2 = True
            client.send(JOIN_REQUEST_FLAG.encode())
            while run2:
                response = client.recv(1024)
                if response.decode() == NEW_USER_FLAG:
                    if taken > 0:
                        print("Username already taken, please pick another username!")
                    USERNAME = input("Enter a username: ")
                    client.send(USERNAME.encode())
                    taken += 1
                elif response.decode() == JOIN_ACCEPT_FLAG:
                    receive_thread = threading.Thread(target=receive)
                    receive_thread.start()
                    #write_thread = threading.Thread(target=write, args=(USERNAME,))
                    #write_thread.start()
                    #run = False
                    write(USERNAME)
                    run2 = False
                    break
                elif response.decode() == JOIN_REJECT_FLAG:
                    print("Chatroom is full try again later")
                    break


        elif choice == "3":
            print("Thank you for using our program!")
            client.send(QUIT_REQUEST_FLAG.encode())
            response = client.recv(1024)
            if(response.decode() == QUIT_ACCEPT_FLAG):
                break
        else:
            print("Invalid choice")


def savefile(FILENAME, file):
    with open(f"downloads/{FILENAME.decode()}", "w") as f:
        f.write(file.decode())
        f.flush()
        f.close()

def receive():
    while True:
        try:
            msg = client.recv(1024)
            if msg.decode() == QUIT_ACCEPT_FLAG:
                break
            elif msg.decode() == ATTACHMENT_FLAG:
                FILENAME = client.recv(1024)
                #print(f"file name: {FILENAME.decode()}")
                file = client.recv(1024)
                #print(f"file contents: {file.decode()}")
                msg = client.recv(1024)
                print(msg.decode())
                save_thread = threading.Thread(target=savefile, args=(FILENAME, file,))
                save_thread.start()
                save_thread.join()
            else:
                print(msg.decode())
        except:
            break


def write(USERNAME):
    time.sleep(.1)
    PAYLOAD = ""
    while PAYLOAD != f"{USERNAME}: q":
        PAYLOAD = f"{USERNAME}: " + input()
        if PAYLOAD != f"{USERNAME}: q":
            if PAYLOAD == f"{USERNAME}: a":
                client.send(ATTACHMENT_FLAG.encode())
                FILENAME = input("Please enter attachment path: ")
                f = open(FILENAME, "rb")
                data = f.read(1024)
                f.close()
                tail = os.path.split(FILENAME)
                time.sleep(.1)
                client.send(tail[1].encode())
                time.sleep(.1)
                client.send(data)
            else:
                current_time = time.strftime("[%H:%M:%S] ")
                client.send((current_time+PAYLOAD).encode())
        else:
            client.send(QUIT_REQUEST_FLAG.encode())
            break
    response = client.recv(1024)
    if(response.decode() == QUIT_ACCEPT_FLAG):
        print("You have left the chatroom")
        client.close()
        return

main()
