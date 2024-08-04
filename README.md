# Java Chat Application

This repository contains a simple multi-client chat application implemented in Java. It includes a server that can handle multiple client connections and facilitate communication between them.

## Features

- **Multi-client support:** The server can handle multiple clients simultaneously.
- **Nicknames:** Clients can set nicknames upon joining the server.
- **Broadcast messaging:** Messages from one client are broadcasted to all connected clients.
- **Special Commands:**
  - `/quit`: Disconnects the client from the server.
  - `/RickRoll`: Sends a *special* message to all clients.

## Getting Started

### Prerequisites

- Java Development Kit (JDK) installed on your system.

### Running the Server

1. Compile the `Server.java` file:
   ```bash
   javac Server.java
   ```

2. Run the server:
   ```bash
   java Server
   ```

   The server listens for client connections on port 3169.

### Running the Client

1. Compile the `Client.java` file:
   ```bash
   javac Client.java
   ```

2. Run the client:
   ```bash
   java Client
   ```

3. When prompted, enter the IP address of the server and your desired nickname.

## How It Works

- **Server:**
  - Listens for incoming client connections.
  - For each client connection, a new `ConnectionHandler` thread is started.
  - Broadcasts messages received from clients to all connected clients.

- **Client:**
  - Connects to the server using the specified IP address and port.
  - Allows users to send messages to the server, which are then broadcasted to other clients.
  - Special commands can be used to quit or send specific messages.

## Contributing

Contributions to this project are welcome. Please open an issue or submit a pull request for any improvements or bug fixes.
