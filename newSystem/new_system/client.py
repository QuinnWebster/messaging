import socket
import threading
import sqlite3
import datetime

def handle_server(server_socket):
    """
    Function to handle incoming messages from the server.
    """
    while True:

        try:
            # Receive message from the server
            message = server_socket.recv(1024).decode()
            if not message:
                break
            
            print(f"Server: {message}")
            add_message("Server", "Client", message)
            
            
            # Check if server sent 'bye' to terminate the connection
            if message.lower() == 'bye':
                break

        except ConnectionResetError:
            break


def send_client_message_with_message(server_socket, message):

    dont_print_flag = False

    if message == "Sending File":
        dont_print_flag = True

 
    
    if not dont_print_flag:
        print(message)
    
    server_socket.send(message.encode())   



def send_client_message(server_socket):
    """
    Function to send messages to the server.
    """
    
    while True:
        # Get user input to send message to server
        message = input("")
        server_socket.send(message.encode())

        # Check if client sent 'bye' to terminate the connection
        if message.lower() == 'bye':
            break

def start_client(host='127.0.0.1', port=12345):
    """
    Function to start the client and connect to the server.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the specified server host and port
        client_socket.connect((host, port))
        print(f"Connected to host {host}with port{port}")

        # Start a thread to handle incoming messages from the server
        server_thread = threading.Thread(target=handle_server, args=(client_socket,))
        server_thread.start()

        # Start a thread to handle sending messages to the server
        send_thread = threading.Thread(target=send_client_message, args=(client_socket,))
        send_thread.start()

        send_thread.join()
        server_thread.join()

    except ConnectionRefusedError:
        print(f"Connection to {host}:{port} refused.")

    finally:
        # Close the client socket
        client_socket.close()
        print("Connection closed.")

def create_connection():

    conn = None
    try:
        conn = sqlite3.connect("messages.db")
        #print("Connection established.")
    except sqlite3.Error as e:
        print(f"Error: {e}")

    return conn

    

def add_message(sender, receiver, message_content):
    conn = create_connection()
    
    if conn is None:
        print("Connection failed.")
        return
    
    try:
        cursor = conn.cursor()

        sql_insert_query = """
            INSERT INTO messages (sender, receiver, message)
            VALUES (?, ?, ?)
        """

        cursor.execute(sql_insert_query, (sender, receiver, message_content))

        conn.commit()

        #print("Message added successfully.")

    finally:
        conn.close()
        #print("Connection closed.")


if __name__ == "__main__":
    start_client()
