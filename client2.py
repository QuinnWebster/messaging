import socket
import threading
import sqlite3
import datetime

def adapt_datetime(datetime_obj):
    return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')

sqlite3.register_adapter(datetime.datetime, adapt_datetime)

def handle_server(server_socket):
    while True:
        try:
            message = server_socket.recv(1024).decode()
            if not message:
                break
            print(f"Server: {message}")
        except ConnectionResetError:
            break

def start_client(host='127.0.0.1', port=12345):
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the specified server host and port
        client_socket.connect((host, port))
        print(f"Connected to {host}:{port}")

        # Start a new thread to handle incoming messages from the server
        server_thread = threading.Thread(target=handle_server, args=(client_socket,))
        server_thread.start()

        # Main thread to handle outgoing messages to the server
        while True:
            message = input("")
            timeSent = datetime.datetime.now()
            #print(f"Time sent: {timeSent}")
            add_message("Client", "Server", message, timeSent)
            if message.lower() == 'bye':
                break
            client_socket.send(message.encode())

    except ConnectionRefusedError:
        print(f"Connection to {host}:{port} refused.")

    finally:
        # Close the client socket
        client_socket.close()
        server_thread.join()
        print("Connection closed.")


def create_connection():

    conn = None
    try:
        conn = sqlite3.connect("mydatabase.db")
        #print("Connection established.")
    except sqlite3.Error as e:
        print(f"Error: {e}")

    return conn

    

def add_message(sender, receiver, message_content, time_sent):
    conn = create_connection()
    
    if conn is None:
        print("Connection failed.")
        return
    
    try:
        cursor = conn.cursor()

        sql_insert_query = """
            INSERT INTO messages (sender, receiver, message, time_sent)
            VALUES (?, ?, ?, ?)
        """

        if not isinstance(time_sent, datetime.datetime):
            time_sent = datetime.datetime.strptime(time_sent, "%Y-%m-%d %H:%M:%S")

        cursor.execute(sql_insert_query, (sender, receiver, message_content, time_sent))

        conn.commit()

        #print("Message added successfully.")

    finally:
        conn.close()
        #print("Connection closed.")

if __name__ == "__main__":
    start_client()
