import java.io.*;
import java.net.*;
import java.util.Scanner;
import java.util.concurrent.CopyOnWriteArrayList;

public class ChatApplication {
    private static final int PORT = 12345;
    private static CopyOnWriteArrayList<ClientHandler> clients = new CopyOnWriteArrayList<>();

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.println("Enter 'server' to run as server or 'client' to run as client:");
        String choice = scanner.nextLine().trim().toLowerCase();

        if (choice.equals("server")) {
            runServer();
        } else if (choice.equals("client")) {
            runClient();
        } else {
            System.out.println("Invalid choice. Please enter 'server' or 'client'.");
        }
    }

    public static void runServer() {
        try {
            ServerSocket serverSocket = new ServerSocket(PORT);
            InetAddress ipAddress = InetAddress.getLocalHost();
            String serverAddress = ipAddress.getHostAddress();
            System.out.println("Server is running...");
            System.out.println("Server address: " + serverAddress);
            System.out.println("Server port: " + PORT);

            while (true) {
                Socket clientSocket = serverSocket.accept();
                System.out.println("New client connected: " + clientSocket);

                ClientHandler clientHandler = new ClientHandler(clientSocket);
                clients.add(clientHandler);
                new Thread(clientHandler).start();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void broadcast(String message, ClientHandler sender) {
        for (ClientHandler client : clients) {
            if (client != sender) {
                client.sendMessage(message);
            }
        }
    }

    private static class ClientHandler implements Runnable {
        private Socket clientSocket;
        private PrintWriter out;
        private BufferedReader in;

        public ClientHandler(Socket socket) {
            this.clientSocket = socket;
            try {
                out = new PrintWriter(clientSocket.getOutputStream(), true);
                in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        @Override
        public void run() {
            try {
                String username = getUsername();
                System.out.println("User " + username + " connected.");

                out.println("Welcome to the chat, " + username + "!");
                out.println("Type Your Message");
                String inputLine;

                while ((inputLine = in.readLine()) != null) {
                    System.out.println("[" + username + "]: " + inputLine);
                    broadcast("[" + username + "]: " + inputLine, this);
                }

                clients.remove(this);
                in.close();
                out.close();
                clientSocket.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        private String getUsername() throws IOException {
            out.println("Enter your username:");
            return in.readLine();
        }

        public void sendMessage(String message) {
            out.println(message);
            out.println("Type Your Message");
        }
    }

    public static void runClient() {
        Scanner scanner = new Scanner(System.in);
        System.out.println("Enter the server address (e.g., localhost):");
        String serverAddress = scanner.nextLine().trim();

        try {
            Socket socket = new Socket(serverAddress, PORT);
            System.out.println("Connected to the chat server!");

            PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));

            new Thread(() -> {
                try {
                    String serverResponse;
                    while ((serverResponse = in.readLine()) != null) {
                        System.out.println(serverResponse);
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }).start();

            String userInput;
            while (true) {
                userInput = scanner.nextLine();
                out.println(userInput);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}