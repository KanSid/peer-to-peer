<h1>Structure and Plan</h1>
What You're Building
A local, offline, peer to peer chat and file sharing app
Works on WiFi / LAN with no internet
No central server, no cloud
Like BitChat but over WiFi with file sharing
Core Architecture
Network Type    → WiFi / LAN
Topology        → Single host with election fallback
Discovery       → UDP broadcast (port 5001)
Communication   → TCP direct connections (port 5000)
Security        → Room code + AES-GCM encryption
Platform        → Python, any device
How Peers Connect
Step 1 — User enters room code
Step 2 — App derives room_hash from code
Step 3 — UDP broadcast HELLO + room_hash
Step 4 — Existing peers verify hash, reply with HELLO_ACK
Step 5 — TCP connection opened to every peer
Step 6 — Full mesh formed
Security Model
Room code → gates who can discover the room
AES-GCM   → encrypts all messages and files
room_hash → never exposes actual room code in packets

HELLO packet:
{
    "type": "HELLO",
    "room_hash": "a3f9b2c1",   ← hashed, not raw code
    "device_id": "f47ac10b",
    "name": "Arjun",
    "port": 5000
}
Identity Model
Device ID   → generated once on install, permanent
Name        → user picks, can change anytime
Display     → "Arjun #f47" (name + last 3 of device ID)
Duplicate names → distinguished by #xyz suffix
Stored in   → config.json on device
Host Election System
Three layer fallback:

Layer 1 — Voluntary handoff
Host wants to leave
Broadcasts WANT_HOST?
First peer to accept becomes host
Host leaves cleanly

Layer 2 — Crash detection
Host dies silently
Peers detect via heartbeat timeout (15 seconds)
Lowest IP peer broadcasts WANT_HOST?
First to accept becomes host

Layer 3 — Automatic fallback
Nobody accepts in 10 seconds
Lowest IP peer automatically becomes host
No human input needed
Chat Model
Group chat → message goes to all peers
DM         → message goes to one peer only
DM request → must be accepted before chatting
Declined   → 5 minute cooldown before re-request
File Sharing Model
Group share → everyone sees, anyone downloads
DM share    → only target sees and downloads
Transfer    → direct peer to peer TCP
Method      → chunked (1024 bytes)
Integrity   → MD5 checksum at end
Interrupted → restart from beginning
Tracking    → unique file_id per transfer
Message History
Storage     → SQLite locally on each device
Scope       → per room (separate per room code)
New joiners → see messages from join point only
No syncing  → history never shared between peers
Limit       → last 1000 messages per room
DMs         → stored privately on both devices only
Protocol Message Types
Discovery:
HELLO              → announce joining
HELLO_ACK          → respond to new peer

Host Election:
WANT_HOST?         → request for new host
ILL_DO_IT          → volunteer response
NEW_HOST           → confirm new host
HOST_ALIVE         → heartbeat every 5 seconds

Chat:
MSG                → group or DM message

DM:
DM_REQUEST         → request to DM someone
DM_RESPONSE        → accept or decline

File:
FILE_ANNOUNCE      → share a file
FILE_REQUEST       → request to download
FILE_CHUNK         → chunk of file data
FILE_DONE          → transfer complete + checksum

Exit:
BYE                → clean disconnect
Single Point of Failure Analysis
Any single peer     → ❌ Not a SPOF (mesh design)
Room code           → ❌ Not a SPOF (security boundary)
Peer list           → ❌ Not a SPOF (every peer has copy)
UDP discovery       → ⚠️  Partial (manual IP fallback)
Message delivery    → ⚠️  Partial (store and forward)
WiFi network        → ✅  Yes, infrastructure SPOF
                         Accepted design constraint
Folder Structure
LocalChat/
│
├── main.py                  → entry point
├── config.json              → device ID, name, settings
│
├── core/
│   ├── peer_manager.py      → tracks peers, connections
│   ├── discovery.py         → UDP broadcast
│   ├── server.py            → TCP server, one thread per peer
│   ├── client.py            → outgoing TCP connections
│   └── election.py          → host election logic
│
├── features/
│   ├── chat.py              → group and DM messages
│   ├── file_transfer.py     → chunked transfer + checksum
│   └── protocol.py          → all message types defined here
│
├── storage/
│   ├── database.py          → SQLite operations
│   └── messages.db          → local message history
│
├── ui/
│   ├── app.py               → PyQt5 main window
│   ├── launch_screen.py     → name + room code entry
│   ├── chat_screen.py       → main chat UI
│   └── dm_screen.py         → DM conversations
│
└── utils/
    ├── crypto.py            → AES encryption, room hash
    ├── framing.py           → TCP message framing
    └── checksum.py          → MD5 file integrity
Technology Stack
Language        → Python 3
UI              → PyQt5
Communication   → TCP + UDP sockets
Concurrency     → threading
Protocol        → JSON over TCP
Encryption      → AES-GCM (cryptography library)
Storage         → SQLite (built into Python)
File Transfer   → TCP chunked stream
Network         → WiFi / LAN
UI Summary
Framework  → PyQt5
Screens    → Launch, Chat, DM (inline file cards)
Style      → Telegram inspired, clean minimal
Palette:
   Background   #FFFFFF
   Sidebar      #F4F4F5
   Sent msg     #EFFDDE
   Accent       #2AABEE
   Text         #1A1A1A
   Subtle text  #999999
Build Order (Recommended)
Phase 1 — Core (get two devices talking)
   UDP discovery
   TCP connection
   Basic group chat

Phase 2 — Features
   Host election
   DM system
   File transfer
   SQLite history

Phase 3 — Polish
   PyQt5 UI
   Progress bars
   Join / leave notifications
   Network health monitor
   Auto reconnect
How This Compares to BitChat
BitChat              Your App
───────              ────────
Bluetooth mesh       WiFi / LAN
~10m per hop         ~50m range
Mobile only          Any device
No file sharing      File sharing ✅
Open to anyone       Room code gated ✅
Signal protocol      AES-GCM + room code
Complex codebase     Clean modular Python
