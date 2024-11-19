import socket
import threading
import os
import sqlite3


def handle_client(client_socket):
    """
    Function to handle incoming messages from the client.
    """

    add_to_db = True

    while True:
        try:
            # Receive message from the client
            message = client_socket.recv(1024).decode()
            if not message:
                break
            print(f"Client: {message}")

            if(message == "Ready to receive file"):

                #add_to_db = False

                send_server_message_with_message(client_socket, "Sending File")

                send_file(client_socket, "test.txt")

            if(message == "ACK_I"):
                send_server_message_with_message(client_socket, "Sending Photo")
                send_photo(client_socket, "photo.jpg")
            

            if add_to_db:
                add_message("Client", "Server", message)

            add_to_db = True


            # Check if client sent 'bye' to terminate the connection
            if message.lower() == 'bye':
                break

           

        except ConnectionResetError:
            break


def send_file(client_socket, filename):
    """
    Function to send a file to the client.
    """

    file_size = os.path.getsize(filename)

    client_socket.send(str(file_size).encode())

    with open(filename, 'rb') as file:
        while True:
            # Read 1024 bytes of data from the file
            data = file.read(1024)
            if not data:
                break
            # Send the data to the client
            client_socket.send(data)

    file.close()

def send_photo(client_socket, imageName):
    """
    Function to send a file to the client.
    """

    file_size = os.path.getsize(imageName)

    client_socket.send(str(file_size).encode())

    with open(imageName, 'rb') as file:
        while True:
            # Read 1024 bytes of data from the file
            data = file.read(1024)
            if not data:
                break
            # Send the data to the client
            client_socket.send(data)

    file.close()


def send_server_message_with_message(client_socket, message):

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
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Bind the server socket to the host and port
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"Server listening on {host}:{port}...")

        # Accept a client connection
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")

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
            print('here')
            print(row)

    finally:
        conn.close()
        #print("Connection closed.")


if __name__ == "__main__":

    conn = create_connection()

    if conn is not None:
        create_table(conn)
    else:
        print("Connection failed.")

    start_server()

    read_all_messages()
