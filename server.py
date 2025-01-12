import socket
import threading
import mysql.connector
import hashlib
from datetime import datetime

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'azaz',
    'database': 'chat_db'
}

class ChatServer:
    def __init__(self):
        self.clients = {}  # {client_socket: {'user_id': ..., 'username': ..., 'current_room': ..., 'current_dm': ...}}

    def connect_db(self):
        return mysql.connector.connect(**db_config)

    def register_user(self, username, password):
        conn = self.connect_db()
        cursor = conn.cursor()
        try:
            hashed_pass = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_pass))
            conn.commit()
            return True
        except mysql.connector.IntegrityError:
            return False
        finally:
            conn.close()

    def login_user(self, username, password):
        conn = self.connect_db()
        cursor = conn.cursor()
        try:
            hashed_pass = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute("SELECT id FROM users WHERE username = %s AND password = %s", (username, hashed_pass))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            conn.close()

    def get_username_by_id(self, user_id):
        """
        Return the username for the given user_id.
        If not found, return something sensible like "<unknown>".
        """
        conn = self.connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            if result:
                return result[0]
            return "<unknown>"
        finally:
            conn.close()

    def save_message(self, sender_id, content, room_id=None, receiver_id=None):
        conn = self.connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO messages (sender_id, content, room_id, receiver_id, timestamp)
                VALUES (%s, %s, %s, %s, %s)
            """, (sender_id, content, room_id, receiver_id, datetime.now()))
            conn.commit()
        finally:
            conn.close()

    def get_dm_history(self, sender_id, receiver_id):
        conn = self.connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT u.username, m.content, m.timestamp
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE (m.sender_id = %s AND m.receiver_id = %s)
                   OR (m.sender_id = %s AND m.receiver_id = %s)
                ORDER BY m.timestamp ASC
            """, (sender_id, receiver_id, receiver_id, sender_id))
            return cursor.fetchall()
        finally:
            conn.close()

    def get_room_history(self, room_name):
        conn = self.connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT u.username, m.content, m.timestamp
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                JOIN rooms r ON m.room_id = r.id
                WHERE r.name = %s
                ORDER BY m.timestamp ASC
            """, (room_name,))
            return cursor.fetchall()
        finally:
            conn.close()

    def handle_client(self, client_socket):
        """
        Each client connection is handled here.
        """
        user_data = {'user_id': None, 'username': None, 'current_room': None, 'current_dm': None}

        # ---------------------
        # Helper UI functions
        # ---------------------
        def send_message(msg):
            """
            Safely send a message to the client, encoded in UTF-8.
            Adds a newline for clarity.
            """
            client_socket.send((msg + "\n").encode())

        def format_history(history):
            """
            Convert a list of (username, content, timestamp) into a formatted multiline string.
            """
            lines = []
            for msg in history:
                time_str = msg[2].strftime("%Y-%m-%d %H:%M:%S")
                lines.append(f"[{time_str}] {msg[0]}: {msg[1]}")
            return "\n".join(lines)

        def fancy_header(title):
            """
            Returns a string with a simple ASCII banner for a given title.
            """
            bar = "+" + "-"*(len(title)+4) + "+"
            return f"{bar}\n|  {title}  |\n{bar}"

        def show_welcome_message():
            """
            First prompt to show upon client connection.
            """
            send_message(fancy_header(" WELCOME TO THE CHAT "))
            send_message("Type '/register <username> <password>' to create a new account.\n"
                         "Or '/login <username> <password>' if you already have an account.\n")

        def show_main_menu():
            """
            Show the main menu with available commands after user logs in.
            """
            send_message("\n" + fancy_header(" MAIN MENU "))
            send_message("Available commands:\n"
                         "  /join <room>       - Join or create a chat room\n"
                         "  /dm <username>     - Start a private chat\n"
                         "  /help              - Show command list again\n"
                         "  /back              - Return to this main menu\n"
                         "  /exit              - Logout from the chat\n"
                         "------------------------------------"
                         "\nPlease type a command:\n> ")

        # ---------------------
        # Initial welcome
        # ---------------------
        show_welcome_message()

        while True:
            try:
                message = client_socket.recv(1024).decode().strip()
                if not message:
                    break

                # --------------------------------------------------
                # Handle commands (those starting with '/')
                # --------------------------------------------------
                if message.startswith('/'):
                    parts = message.split()
                    command = parts[0]

                    # /register <username> <password>
                    if command == '/register' and len(parts) == 3:
                        username = parts[1]
                        password = parts[2]
                        if self.register_user(username, password):
                            send_message("Registration successful! Please login with '/login <username> <password>'.")
                        else:
                            send_message("Registration failed. Username may be taken.")

                    # /login <username> <password>
                    elif command == '/login' and len(parts) == 3:
                        username = parts[1]
                        password = parts[2]
                        user_id = self.login_user(username, password)
                        if user_id:
                            user_data['user_id'] = user_id
                            user_data['username'] = username
                            self.clients[client_socket] = user_data
                            send_message(f"Login successful! Welcome, {username}!")
                            show_main_menu()
                        else:
                            send_message("Login failed. Check your credentials.")

                    # /join <room_name>
                    elif command == '/join' and len(parts) == 2:
                        room_name = parts[1]
                        # Create room if doesn't exist
                        conn = self.connect_db()
                        cursor = conn.cursor()
                        cursor.execute("INSERT IGNORE INTO rooms (name) VALUES (%s)", (room_name,))
                        conn.commit()
                        cursor.execute("SELECT id FROM rooms WHERE name = %s", (room_name,))
                        room_id = cursor.fetchone()[0]
                        conn.close()

                        user_data['current_room'] = room_name
                        user_data['current_dm'] = None

                        send_message(f"\nYou have joined room: {room_name}")
                        send_message("Fetching room history...\n")

                        history = self.get_room_history(room_name)
                        if history:
                            send_message(format_history(history))
                        else:
                            send_message("No previous messages in this room.\n")

                        send_message("Type your message below. Or type '/back' to return to Main Menu.\n")

                    # /dm <username>
                    elif command == '/dm' and len(parts) == 2:
                        target_user = parts[1]
                        conn = self.connect_db()
                        cursor = conn.cursor()
                        cursor.execute("SELECT id FROM users WHERE username = %s", (target_user,))
                        result = cursor.fetchone()
                        conn.close()

                        if result:
                            receiver_id = result[0]
                            user_data['current_dm'] = receiver_id
                            user_data['current_room'] = None

                            send_message(f"\nStarting private chat with {target_user}...")
                            send_message("Fetching private chat history...\n")

                            history = self.get_dm_history(user_data['user_id'], receiver_id)
                            if history:
                                send_message(format_history(history))
                            else:
                                send_message("No previous private messages.\n")

                            send_message("Type your message below. Or type '/back' to return to Main Menu.\n")
                        else:
                            send_message(f"User '{target_user}' not found.\n")

                    # /help
                    elif command == '/help':
                        help_text = (
                            "\n" + fancy_header(" HELP MENU ") + "\n"
                            "Commands:\n"
                            "  /join <room>       - Join a chat room\n"
                            "  /dm <username>     - Start a private chat\n"
                            "  /back              - Return to main menu\n"
                            "  /exit              - Logout\n"
                            "------------------------------------"
                            "\nType your choice:\n"
                        )
                        send_message(help_text)

                    # /back
                    elif command == '/back':
                        user_data['current_room'] = None
                        user_data['current_dm'] = None
                        show_main_menu()

                    # /exit
                    elif command == '/exit':
                        send_message("You have been logged out. Goodbye!")
                        break

                    else:
                        send_message("Unknown command or invalid usage. Type '/help' for assistance.\n")

                # --------------------------------------------------
                # Handle regular messages (not starting with '/')
                # --------------------------------------------------
                else:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    sender_name = user_data['username']

                    # --- CASE 1: User is in a room ---
                    if user_data['current_room']:
                        # Get the room_id from the DB
                        conn = self.connect_db()
                        cursor = conn.cursor()
                        cursor.execute("SELECT id FROM rooms WHERE name = %s", (user_data['current_room'],))
                        room_id = cursor.fetchone()[0]
                        conn.close()

                        # 1. Save to DB
                        self.save_message(user_data['user_id'], message, room_id=room_id)

                        # 2. Broadcast only to users who are in the same room
                        for client, data in self.clients.items():
                            if data['current_room'] == user_data['current_room']:
                                client.send(
                                    f"[{timestamp}] {sender_name} (Room:{user_data['current_room']}): {message}\n".encode()
                                )

                    # --- CASE 2: User is in a DM ---
                    elif user_data['current_dm']:
                        # Look up the recipient's username
                        recipient_id = user_data['current_dm']
                        recipient_name = self.get_username_by_id(recipient_id)

                        # 1. Save DM in DB
                        self.save_message(user_data['user_id'], message, receiver_id=recipient_id)

                        # 2. Show message to the sender in their own terminal
                        #    (We say "DM to <recipient_name>").
                        client_socket.send(
                            f"[{timestamp}] DM to {recipient_name}: {message}\n".encode()
                        )

                        # 3. Check if the receiver is also in the DM with this sender
                        for client, data in self.clients.items():
                            # If we find the receiver
                            if data['user_id'] == recipient_id:
                                # Check if they are actively in a DM with the sender
                                if data['current_dm'] == user_data['user_id']:
                                    # DM from <sender_name>
                                    client.send(
                                        f"[{timestamp}] DM from {sender_name}: {message}\n".encode()
                                    )

                    # --- CASE 3: User is not in room or DM ---
                    else:
                        send_message("You're not in a room or DM. Type '/back' to return to main menu.\n")

            except Exception as e:
                print(f"Error: {e}")
                break

        # Remove client from self.clients upon disconnection
        if client_socket in self.clients:
            del self.clients[client_socket]
        client_socket.close()

    def start(self, host="127.0.0.1", port=5550):
        """
        Starts the chat server on the specified host and port.
        """
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen()
        print(f"Server running on {host}:{port}")

        while True:
            client_socket, _ = server.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    ChatServer().start()



    
        
