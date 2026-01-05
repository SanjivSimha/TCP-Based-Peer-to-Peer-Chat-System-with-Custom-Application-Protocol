import socket
import argparse
import sys
import select

def server(c, clientCount):
    global c1_id
    global c1_ip
    global c1_port
    
    sockets, __, __ = select.select([c, sys.stdin], [], [])
    for x in sockets:
        if x is sys.stdin:
            print("running sys.stdin")
            msg = sys.stdin.readline().rstrip("\n")
            if (msg == "/info"):
                if clientCount == 1:
                    print(f"{client_id} {client_ip}:{client_port}")
                elif clientCount == 2:
                    print(f"{client_id} {client_ip}:{client_port}\n{c1_id} {c1_ip}:{c1_port}")
        elif x is c:
            message = c.recv(1024).decode()
            lines = message.split("\r\n")
            if lines[0].strip() == "REGISTER":
                #parse client id, ip, port
                client_id = lines[1].split(":")[1].strip()
                client_ip = lines[2].split(":")[1].strip()
                client_port = int(lines[3].split(":")[1].strip())
                print(f"REGISTER: {client_id} from {client_ip}:{client_port} received")
                clientCount += 1 #record client
                message = f"REGACK\r\nclientID: {client_id}\r\nIP: {client_ip}\r\nPort: {client_port}\r\n\r\n"
                c.send(message.encode()) #send REGACK
                if clientCount == 1:
                    c1_id = client_id
                    c1_ip = client_ip
                    c1_port = client_port

            message = c.recv(1024).decode()
            lines = message.split("\r\n")

            if lines[0].strip() == "BRIDGE":
                client_id = lines[1].split(":")[1].strip()
                if clientCount == 1:
                    print(f"BRIDGE: {client_id} {client_ip}:{client_port}")
                    message = f"BRIDGEACK\r\nclientID: \r\nIP: \r\nPort: \r\n\r\n"
                    c.send(message.encode())
                if clientCount == 2:
                    print(f"BRIDGE: {c1_id} {c1_ip}:{c1_port} {client_id} {client_ip}:{client_port}")
                    message = f"BRIDGEACK\r\nclientID: {c1_id}\r\nIP: {c1_ip}\r\nPort: {c1_port}\r\n\r\n"
                    c.send(message.encode())
            
            if lines[0].strip() not in ("REGISTER", "BRIDGE"):
                print("Malformed incoming message", file=sys.stderr)
        else:
            print("else")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()
    serverPort = int(args.port)
    try:
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print("socket creation failed")
        sys.exit(1)

    try:
        serverSocket.bind(('127.0.0.1', serverPort))
    except socket.error:
        print("socket bind failed")
        sys.exit(1)


    try:
        serverSocket.listen(5)
        print(f"Server is listening on {serverSocket.getsockname()[0]}:{serverSocket.getsockname()[1]}")
        clientCount = 0 #client recorded var
        #c1_id = ""
        #c1_ip = ""
        #c1_port = ""
        while True:
            global c1_id
            global c1_ip
            global c1_port

            sockets, __, __ = select.select([serverSocket, sys.stdin], [], [])
            
            for x in sockets:
                if x is sys.stdin:
                    msg = sys.stdin.readline().rstrip("\n")
                    if (msg == "/info"):
                        if clientCount == 1:
                            print(f"{client_id} {client_ip}:{client_port}")
                        elif clientCount == 2:
                            print(f"{client_id} {client_ip}:{client_port}\n{c1_id} {c1_ip}:{c1_port}")
                elif x is serverSocket:
                    c, addr = serverSocket.accept()
                    message = c.recv(1024).decode()
                    lines = message.split("\r\n")
                    if lines[0].strip() == "REGISTER":
                        #parse client id, ip, port
                        client_id = lines[1].split(":")[1].strip()
                        client_ip = lines[2].split(":")[1].strip()
                        client_port = int(lines[3].split(":")[1].strip())
                        print(f"REGISTER: {client_id} from {client_ip}:{client_port} received")
                        clientCount += 1 #record client
                        message = f"REGACK\r\nclientID: {client_id}\r\nIP: {client_ip}\r\nPort: {client_port}\r\n\r\n"
                        c.send(message.encode()) #send REGACK
                        if clientCount == 1:
                            c1_id = client_id
                            c1_ip = client_ip
                            c1_port = client_port

                    message = c.recv(1024).decode()
                    lines = message.split("\r\n")

                    if lines[0].strip() == "BRIDGE":
                        client_id = lines[1].split(":")[1].strip()
                        if clientCount == 1:
                            print(f"BRIDGE: {client_id} {client_ip}:{client_port}")
                            message = f"BRIDGEACK\r\nclientID: \r\nIP: \r\nPort: \r\n\r\n"
                            c.send(message.encode())
                        if clientCount == 2:
                            print(f"BRIDGE: {c1_id} {c1_ip}:{c1_port} {client_id} {client_ip}:{client_port}")
                            message = f"BRIDGEACK\r\nclientID: {c1_id}\r\nIP: {c1_ip}\r\nPort: {c1_port}\r\n\r\n"
                            c.send(message.encode())
                    
                    if lines[0].strip() == "QUIT":
                        serverSocket.close()
                        sys.exit(0)
                            
                    
                    if lines[0].strip() not in ("REGISTER", "BRIDGE", "QUIT"):
                        print("Malformed incoming message", file=sys.stderr)
    except KeyboardInterrupt:
        serverSocket.close()
        sys.exit(0)

if __name__ == "__main__":
    main()