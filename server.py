import socket
import sys
import os


# Read the specified file on the server-side.
def read_file(file_path, client_socket):
    # Create the full path of the file.
    full_path = "files" + file_path
    # If the file is a picture, read it in binary mode.
    if full_path.endswith("jpg") or full_path.endswith("ico"):
        reading_mode = "rb"
    # Else - read it in regular text format.
    else:
        reading_mode = "r"
    try:
	# Open the file, read it and return its content and its size.
        with open(full_path, mode=reading_mode) as target_file:
            file_content = target_file.read()
            return file_content, os.path.getsize(full_path)
    # If an error occurred during opening or reading the file - handle it.
    except IOError:
	# Send a 404 Not Found error message to the client and close the socket.
        error_msg = "HTTP/1.1 404 Not Found\r\n' + Connection: close\r\n"
        client_socket.send(error_msg)
        client_socket.close()
        return IOError, -1

		
# Handle a client's request.
def handle_client_request(client_socket, client_request):
    # Split the client's request to lines.
    data = client_request.split("\r\n")
    first_line = data[0]
    # The file path is the first word after the first space in the first line.
    file_path = first_line.split(" ")[1]
    # If it's a redirection request, send a redirection response and close the socket.
    if file_path == "/redirect":
        error_msg = "HTTP/1.1 301 Moved Permanently\r\n" + "Connection: close\r\n" + "Location: /result.html\r\n\r\n"
        client_socket.send(error_msg)
        client_socket.close()
        return False
    # The meaning of the path / is the file index.html.
    if file_path == '/':
        file_path = "/index.html"
    # Read the file and get its content and its length.
    file_content, file_len = read_file(file_path, client_socket)
    # If an error occurred during opening or reading the file - return False that indicates the socket was closed.
    if file_content == IOError:
        return False
    # Find the line that starts with the word "Connection".
    for line in data:
        if line.startswith("Connection"):
            break
    line = line.split(" ")
    # The first word after the first space in the first line is the type of connection (keep-alive or close).
    connection = line[1]
    # Send a 200 OK response.
    server_response = "HTTP/1.1 200 OK\r\n" + "Connection: " + connection + "\r\n" + "Content-Length: " + str(file_len)\
        + "\r\n\r\n"
    # The content of the file appears after an empty line.
    server_response = server_response + file_content
    client_socket.send(server_response)
    # If the connection is close - close the socket and return False.
    if connection == "close":
        client_socket.close()
        return False
    # Else - the connection is keep-alive - don't close the socket and return True.
	return True

	
# Read the request of the client, print it to the screen, and handle it.
def read_client_request(client_socket):
    client_request = ""
    # The end of the request is marked by '\r\n\r\n'.
    while not client_request.endswith('\r\n\r\n'):
        try:
            # Set a timeout of 1 second on socket operations.
            client_socket.settimeout(1)
            # Read 4096 bytes from the socket.
            client_request += client_socket.recv(4096)
        # Close the socket after 1 second of no response.
        except socket.timeout:
            client_socket.close()
            # Return False, which indicates that the socket was closed.
            return False
    # Print the client's request to the screen.
    print client_request
    # Handle the client's request.
    connection = handle_client_request(client_socket, client_request)
    # If the connection is keep-alive, return True, otherwise - return False.
    return connection


def main():
    # Create a welcoming TCP socket.
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # The first argument to main is the source port of the server.
    source_port = int(sys.argv[1])
    # The source IP of the server.
    source_ip = '127.0.0.1'
    # Bind the socket to the source IP & the source port.
    server_socket.bind((source_ip, int(source_port)))
    # Set the maximum number of unaccepted connections that the system will allow before refusing new connections.
    server_socket.listen(5)
    # Handle clients' requests.
    while True:
	# Create a new separate client socket.
        client_socket, client_address = server_socket.accept()
        client_socket.settimeout(1)
        connection = True
        # As long as the connection is keep-alive - handle the client's requests and don't close the socket.
        while connection:
            connection = read_client_request(client_socket)


if __name__ == "__main__":
    main()
