import argparse
import socket
import sys
import select

def quit_mode(id):
    print(f"{id} has ended the chat session.\nExiting program")
    sys.exit(0)

def chat_mode(mode, s, id, port, ip, peer_id):
    try:
        while True:
            if mode == "READ":
                print("IN READ MODE")
            elif mode == "WRITE":
                print("IN WRITE MODE")
            sockets, __, __ = select.select([s, sys.stdin], [], [])

            for x in sockets:
                if x is s:
                    if mode == "QUIT":
                        s.close()
                        quit_mode(peer_id)
                    if mode == "READ":
                        data = s.recv(1024).decode()
                        new_data = data.split("\r\n")
                        msg_type = new_data[0]
                        if msg_type == "QUIT":
                            peer_id = new_data[1].split(": ")[1]
                            mode = "QUIT"
                        elif msg_type == "SPECIAL QUIT":
                            print("Keyboard Interrupt closed successfully")
                            sys.exit(0)
                        else:
                            peer_id = new_data[1].split(": ")[1]
                            text = new_data[4].split(": ")[1].replace("\r\n", "")
                            if len(text) != 0:
                                print(f"{peer_id}> {text}")
                            mode = "WRITE"
                
                elif x is sys.stdin:
                    msg = sys.stdin.readline().rstrip("\n")
                    if (msg == "/quit"):
                        # quit for self program
                        print("Chat session ended\nExiting program")
                        data = f"QUIT\r\nid: {id}\r\n\r\n"
                        s.send(data.encode())
                        s.close()
                        sys.exit(0)
                    elif mode == "WRITE":
                        data = f"CHAT\r\nid: {id}\r\nIP: {ip}\r\nport: {port}\r\ntext: {msg}\r\n\r\n"
                        s.send(data.encode())
                        mode = "READ"
    except KeyboardInterrupt:
        data = "SPECIAL QUIT\r\n: {id}\r\n\r\n"
        s.send(data.encode())
        print("Keyboard Interrupt closed successfully")
        sys.exit(0)

def main():
    # parse arguments
    parser = argparse.ArgumentParser()

    # add arguments
    parser.add_argument("--id", type=str)
    parser.add_argument("--port", type=int)
    parser.add_argument("--server", type=str)

    args = parser.parse_args()

    server_ip, server_port = args.server.split(":")
    server_port = int(server_port)
    args.port = int(args.port)

    #print(f"ID: {args.id}\nPort: {args.port}\nServer IP: {args.server}")

    # connect sockets
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, server_port))
    
    address_list = s.getsockname()
    address = address_list[0]
    #address = "127.0.1.1"

    # info of other client to chat to
    peer_id = ""
    peer_ip = ""
    peer = 0

    print(f"{args.id} running on {address}:{args.port}")

    # indefinitely accept input
    while True:
        try:
            command = input()
            if (command == "/id"):
                print(args.id)
            elif (command == "/register"):
                data = f"REGISTER\r\nclientID: {args.id}\r\nIP: {address}\r\nPort: {args.port}\r\n\r\n"
                s.send(data.encode())
                ack = s.recv(1024)
                ack = ack.decode()
            elif (command == "/bridge"):
                data = f"BRIDGE\r\nclientID: {args.id}\r\n\r\n"
                s.send(data.encode())
                
                # 0 = BRIDGEACK, 1 = ID, 2 = IP, 3 = Port ...
                ack = s.recv(1024)
                ack = ack.decode()
                ack_info = ack.split("\r\n")

                s.close()

                name = ack_info[1].split(": ")[1]
                IP = ack_info[2].split(": ")[1]
                port = ack_info[3].split(": ")[1]

                #print(f"Name: {name}, IP: {IP}, port: {port}")
                
                # if there is no other client to chat with
                if len(name) == 0:
                    print(f"{args.id} IN WAIT MODE")

                    ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    ls.bind((address, args.port))
                    ls.listen(5)
                    conn, addr = ls.accept()
                    with conn:
                        print("IN READ MODE")
                        info = conn.recv(1024).decode()
                        new_info = info.split("\r\n")
                        peer_id = new_info[0].split(": ")[1]
                        peer_ip = new_info[1].split(": ")[1]
                        peer_port = new_info[2].split(": ")[1]
                        #print(f"Incoming chat request from {peer_id} {peer_ip}:{peer_port}")

                        data = conn.recv(1024).decode()
                        new_data = data.split("\r\n", 4)
                        id = new_data[1].split(": ")[1]
                        ip = new_data[2].split(": ")[1]
                        port = new_data[3].split(": ")[1]
                        text = new_data[4].split(": ")[1].replace("\r\n\r\n", "")

                        print(f"Incoming chat request from {id} {ip}:{port}")
                        print(f"{id}> {text}")
                        chat_mode("WRITE", conn, args.id, args.port, address, peer_id)
                        
                # there is a client to chat with
                else:
                    peer_id = name
                    peer_ip = IP
                    peer_port = int(port)
            elif (command == "/chat"):
                ws = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ws.connect((peer_ip, peer_port))

                #text = input()
                print("IN CHAT MODE")
                print("IN WRITE MODE")
                info = f"ID: {args.id}\r\nIP: {address}\r\nPort: {args.port}\r\n\r\n"
                ws.send(info.encode())

                msg = input()
                data = f"CHAT\r\nid: {args.id}\r\nIP: {address}\r\nport: {args.port}\r\ntext: {msg}\r\n\r\n"
                ws.send(data.encode())
                chat_mode("READ", ws, args.id, args.port, address, peer_id)
            elif (command == "/quit"):
                print("quitting before chat")
                quit_message = f"QUIT\r\n\r\n"
                #s.send(quit_message.encode())
                s.close()
                sys.exit(0)       

            else:
                print("Wrong command!")
        except KeyboardInterrupt:
            sys.exit(0)

if __name__ == "__main__":
    main()