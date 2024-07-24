import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class Server implements Runnable {

    private ArrayList<ConnectionHandler> connections;
    private ServerSocket server;
    private boolean done;
    private ExecutorService pool;

    public Server() {
        connections = new ArrayList<>();
        done = false;
    }

    @Override
    public void run() {
        try {
            server = new ServerSocket(3169);
            pool = Executors.newCachedThreadPool();
            while (!done) {
                Socket client = server.accept();
                ConnectionHandler handler = new ConnectionHandler(client);
                connections.add(handler);
                pool.execute(handler);
            }
        } catch (Exception e) {
            shutdown();
        }
    }

    public void broadcast(String message) {
        for (ConnectionHandler ch : connections) {
            if (ch != null) {
                ch.sendMessage(message);
            }
        }
    }

    public void shutdown() {
        try {
            done = true;
            if (!server.isClosed()) {
                server.close();
            }
            for (ConnectionHandler ch : connections) {
                ch.shutdown();
            }
        } catch (IOException e) {
            System.out.println("AAAAAAAAAAAAAAAAAA");
        }
    }

    class ConnectionHandler implements Runnable {

        private Socket client;
        private BufferedReader in;
        private PrintWriter out;
        private String name;

        public ConnectionHandler(Socket client) {
            this.client = client;
        }

        @Override
        public void run() {
            try {
                out = new PrintWriter(client.getOutputStream(), true);
                in = new BufferedReader(new InputStreamReader(client.getInputStream()));
                out.println("Enter your nickname: ");
                name = in.readLine();
                if (name == "Ali Sahin") {
                    System.out.println("THE UNIBROW HAS BEEN UNITED WITH THE SERVER");
                } else if (name == "ali sahin") {
                    System.out.println("THE UNIBROW HAS BEEN UNITED WITH THE SERVER");
                } else {
                    System.out.println(name + "connected");
                }
                broadcast(name + "Joined the server.");
                String message;
                while ((message = in.readLine()) != null) {
                    if (message.startsWith("/quit")) {
                        broadcast(name + "Has left the chat.");
                        shutdown();
                    } else if (message.startsWith("/RickRoll")) {
                        broadcast(name + "tinyurl.com/5x2bcwyj");
                    } else {
                        broadcast(name + ":" + message);
                    }
                }

            } catch (IOException e) {
                shutdown();
            }
        }

        public void sendMessage(String message) {
            out.println(message);
        }

        public void shutdown() {
            try {
                in.close();
                out.close();
                if (!client.isClosed()) {
                    client.close();
                }
            } catch (IOException e) {
                System.out.println("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB");
            }
        }

    }

    public static void main(String[] args) {
        Server server = new Server();
        server.run();
    }
}
