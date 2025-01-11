import socket
import threading

class ChatClient:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def receive_messages(self):
        while True:
            try:
                message = self.client.recv(1024).decode()
                print(f"\n{message}")
                print("> ", end='', flush=True)
            except ConnectionAbortedError:
                break

    def start(self, host="127.0.0.1", port=5550):
        self.client.connect((host, port))
        threading.Thread(target=self.receive_messages, daemon=True).start()

        while True:
            msg = input("> ")
            if msg.lower() == '/exit':
                self.client.close()
                break
            self.client.send(msg.encode())

if __name__ == "__main__":
    ChatClient().start()
