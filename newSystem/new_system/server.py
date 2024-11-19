import socket
import threading
import os
import sqlite3
import datetime



def handle_client(client_socket):
    """
    Function to handle incoming messages from the client.
    """
    while True:

        dont_print_flag = False
        dont_add_to_db_flag = False
        try:
            # Receive message from the client
            message = client_socket.recv(1024).decode()

            if not message:
                break

            print(f"Client: {message}")

            add_message("Client", "Server", message)
            
            # Check if client sent 'bye' to terminate the connection
            if message.lower() == 'bye':
                break

        except ConnectionResetError:
            break

def send_server_message_with_message(client_socket, message):

    dont_print_flag = False

    if not dont_print_flag:
        print(message)
    
    client_socket.send(message.encode())



def send_server_message(client_socket):
    """
    Function to send messages to the client.
    """
    while True:
        # Get user input to send message to client
        message = input("")
        client_socket.send(message.encode())

        # Check if server sent 'bye' to terminate the connection
        if message.lower() == 'bye':
            break

def start_server(host='127.0.0.1', port=12345):
    """
    Function to start the server and handle client connections.
    """

    # Create a server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Bind the server socket to the host and port
        #Just set up the server socket
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"Server listening on host {host} with port {port}...")
        #Server is listening for a connection

        # Accept a client connection
        client_socket, client_address = server_socket.accept()
        print(f"Connection established")
        #The server and client are connected

        # Start a thread to handle incoming messages from the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

        # Start a thread to handle sending messages to the client
        send_thread = threading.Thread(target=send_server_message, args=(client_socket,))
        send_thread.start()

        send_thread.join()
        client_thread.join()

    except OSError as e:
        print(f"Error: {e}")

    finally:
        # Close the server socket
        server_socket.close()
        print("Server socket closed.")



def create_connection():
#Function to create a connection to the database
    conn = None
    try:
        conn = sqlite3.connect("messages.db")
        #print("Connection established.")
    except sqlite3.Error as e:
        print(f"Error: {e}")

    return conn

def create_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS messages (
            num_message INTEGER PRIMARY KEY,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            message TEXT NOT NULL
        )""")
        conn.commit()
        #print("Table created successfully.")
    except sqlite3.Error as e:
        print(f"Error: {e}")
        conn.rollback()

    
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

    finally:
        conn.close()
        #print("Connection closed.")


def read_all_messages():

    conn = create_connection()

    if conn is None:
        print("Connection failed.")
        return

    try:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM messages")

        rows = cursor.fetchall()

        for row in rows:
            print(row)

    finally:
        conn.close()
        #print("Connection closed.")


if __name__ == "__main__":

    conn = create_connection()

    if conn is not None:
        create_table(conn)
    else:
        print("Connection to database failed.")

    start_server()

    read_all_messages()
