#TCP-Based Peer-to-Peer Chat System
##Overview

A TCP socket–based chat application featuring a central rendezvous server and direct peer-to-peer messaging. Clients register with the server to discover peers, then establish a persistent TCP connection for half-duplex chat.

Built to demonstrate practical networking fundamentals, protocol design, and connection management.

##Architecture

server.py – Registers clients and provides peer contact information

client.py – Registers with server, requests a peer, and handles direct chat

###Design pattern:
Client–Server (discovery) → Peer-to-Peer (messaging)

##Protocol

Custom application-layer protocol modeled after HTTP-style messages.

###Client → Server
- REGISTER – Advertise client contact info
- BRIDGE – Request peer info

###Server → Client
- REGACK, BRIDGEACK

###Client → Client
- CHAT, QUIT

##Communication Model

Client–Server: non-persistent TCP

Peer–Peer: persistent TCP

Half-duplex chat (read/write alternation)

Graceful termination and FIN detection
