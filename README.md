## Overview  

This is a **client-server chat application** built with Python that logs all messages into an SQLite database.  

### Features  
- **Client-server communication** using sockets.  
- **Message storage and retrieval** with SQLite.  
- Supports **sending messages, text files, and images** between users.  

### Inspiration  
The project idea was inspired by concepts from a **Communication Networks** class. Its design reflects the **TCP handshake process**:  
1. The **client initiates** the conversation.  
2. The **server acknowledges** the initiation.  
3. The **client acknowledges** the server’s response.  
4. Once the handshake is complete, both sides communicate freely.  
