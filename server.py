import socket
import threading
import sqlite3
import datetime

def adapt_datetime(datetime_obj):
    return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")

sqlite3.register_adapter(datetime.datetime, adapt_datetime)

def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            print(f"Client: {message}")
        except ConnectionResetError:
            break

def start_server(host='127.0.0.1', port=12345):
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Bind to the specified host and port
        server_socket.bind((host, port))

        # Now wait for client connection
        server_socket.listen(1)
        print(f"Server listening on {host}:{port}...")

        # Accept a connection
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")

        # Start a new thread to handle incoming messages from the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

        # Main thread to handle outgoing messages to the client
        while True:
            message = input("")
            timeSent = datetime.datetime.now()
            #print(f"Time sent: {timeSent}")
            add_message("Server", "Client", message, timeSent)
            if message.lower() == 'bye':
                break
            client_socket.send(message.encode())

    except OSError as e:
        print(f"Error: {e}")

    finally:
        # Close the server socket
        server_socket.close()
        print("Server socket closed.")


def create_connection():

    conn = None
    try:
        conn = sqlite3.connect("mydatabase.db")
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
            message TEXT NOT NULL,
            time_sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
        )""")
        conn.commit()
        #print("Table created successfully.")
    except sqlite3.Error as e:
        print(f"Error: {e}")
        conn.rollback()


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
    


def read_all_messages():
    """ Read all messages (rows) from the 'messages' table """
    conn = create_connection()
    if conn is None:
        print("Connection failed.")
        return
    
    try:
        cursor = conn.cursor()

        # Select all rows from the 'messages' table
        cursor.execute("SELECT * FROM messages")
        rows = cursor.fetchall()

        if rows:
            #print("All Messages:")
            for row in rows:
                print(row)
        else:
            i = 1 #dummy
            #print("No messages found in the database.")

    except sqlite3.Error as e:
        print(f"Error reading messages: {e}")

    finally:
        conn.close()
        #print("Connection closed.")


if __name__ == "__main__":
    conn = create_connection()

    
    if conn is not None:
        create_table(conn)
        conn.close()
        #print("Connection closed.")
    else:
        print("Connection failed.")
        
    start_server()

    read_all_messages()
    
