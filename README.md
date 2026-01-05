# TCP-Based Peer-to-Peer Chat System
## Overview

A TCP socket–based chat application featuring a central rendezvous server and direct peer-to-peer messaging. Clients register with the server to discover peers, then establish a persistent TCP connection for half-duplex chat.

Built to demonstrate practical networking fundamentals, protocol design, and connection management.

## Architecture

server.py – Registers clients and provides peer contact information

client.py – Registers with server, requests a peer, and handles direct chat

### Design pattern:
Client–Server (discovery) → Peer-to-Peer (messaging)

## Protocol

Custom application-layer protocol modeled after HTTP-style messages.

### Client → Server
- REGISTER – Advertise client contact info
- BRIDGE – Request peer info

### Server → Client
- REGACK, BRIDGEACK

### Client → Client
- CHAT, QUIT

## Communication Model
- Client–Server: non-persistent TCP
- Peer–Peer: persistent TCP
- Half-duplex chat (read/write alternation)
- Graceful termination and FIN detection

## Running (Mininet / Ubuntu)
#### Start server
python3 server.py --port=5555

#### Client 1
python3 client.py --id=Alice --port=3000 --server=127.0.0.1:5555
/register
/bridge

#### Client 2
python3 client.py --id=Bob --port=4000 --server=127.0.0.1:5555
/register
/bridge
/chat

## Key Features
- Custom TCP application protocol
- State-driven client behavior (WAIT / CHAT)
- Robust socket error handling
- Malformed message detection
- Clean connection teardown

##Tech Stack
- Python 3
- TCP sockets
- Mininet (Ubuntu 22.04)
