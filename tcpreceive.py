"""
- NOTE: REPLACE 'N' Below with your section, year, and lab number
- CS2911 - 011
- Fall 2022
- Lab 3 - Message Encoding
- Names: Josh Sopa & Hudson Arney
  - 

A simple TCP server/client pair.

The application protocol is a simple format: For each file uploaded,
the client first sends four (big-endian) bytes indicating the number of lines as an unsigned binary number.

The client then sends each of the lines, terminated only by '\\n' (an ASCII LF byte).

The server responds with 'A' when it accepts the file.

Then the client can send the next file.


Introduction: (Describe the lab in your own words)
    - Our lab works to receive and send TCP messages through the given TCP port number.
    We use sockets in the receive method that first listen for a message, and wait to grab the message.
    Then the send method works to also create a socket and connect that to the server being provided.
    Once connect it gives the option of the amount of messages the user would like to send. The user
    can then send whatever messages they'd like to the receiver. The receiver will take this message data
    in bytes and send it to the create text file method where depending on the number of messages inputted it
    will create that certain number of text files with the messages inside.

Summary: (Summarize your experience with the lab, what you learned, what you liked, what you disliked,
and any suggestions you have for improvement)
    - This lab had a fair bit of challenge which was good, but still fun to code. We learned a lot about
    how TCP messaging works and how to send a receive such messages between computers. We liked that
    the lab was a fair but decent challenge which made the work having a good feeling of pay off once completed.
    We disliked going back and changing code in case a message being sent was something other than ASCII.
    Some suggestions we have wouldn't necessarily be for the lab itself but on the lectures leading up
    to this lab where our understanding of sending messages didn't feel completely fulfilled.



"""

import socket
import time

# Port number definitions
# (May have to be adjusted if they collide with ports in use by other programs/services.)
TCP_PORT = 12111

# Address to listen on when acting as server.
# The address '' means accept any connection for our 'receive' port from any network interface
# on this system (including 'localhost' loopback connection).
LISTEN_ON_INTERFACE = ''

# Address of the 'other' ('server') host that should be connected to for 'send' operations.
# When connecting on one system, use 'localhost'
# When 'sending' to another system, use its IP address (or DNS name if it has one)
# OTHER_HOST = '155.92.x.x'
OTHER_HOST = 'localhost'


def main():
    """
    Allows user to either send or receive bytes
    """
    # Get chosen operation from the user.
    action = input('Select "(1-TS) tcpsend", or "(2-TR) tcpreceive":')
    # Execute the chosen operation.
    if action in ['1', 'TS', 'ts', 'tcpsend']:
        tcp_send(OTHER_HOST, TCP_PORT)
    elif action in ['2', 'TR', 'tr', 'tcpreceive']:
        tcp_receive(TCP_PORT)
    else:
        print('Unknown action: "{0}"'.format(action))


def tcp_send(server_host, server_port):
    """
    - Send multiple messages over a TCP connection to a designated host/port
    - Receive a one-character response from the 'server'
    - Print the received response
    - Close the socket
    
    :param str server_host: name of the server host machine
    :param int server_port: port number on server to send to
    - Author: Hudson and Josh
    """
    print('tcp_send: dst_host="{0}", dst_port={1}'.format(server_host, server_port))
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((server_host, server_port))

    num_lines = int(input('Enter the number of lines you want to send (0 to exit):'))

    while num_lines != 0:
        print('Now enter all the lines of your message')
        # This client code does not completely conform to the specification.
        #
        # In it, I only pack one byte of the range, limiting the number of lines this
        # client can send.
        #
        # While writing tcp_receive, you will need to use a different approach to unpack to meet the specification.
        #
        # Feel free to upgrade this code to handle a higher number of lines, too.
        tcp_socket.sendall(b'\x00\x00')
        time.sleep(1)  # Just to mess with your servers. :-)
        tcp_socket.sendall(b'\x00' + bytes((num_lines,)))

        # Enter the lines of the message. Each line will be sent as it is entered.
        for line_num in range(0, num_lines):
            line = input('')
            tcp_socket.sendall(line.encode() + b'\n')
        tcp_socket.sendall(b'')

        print('Done sending. Awaiting reply.')
        response = tcp_socket.recv(1)
        if response == b'A':  # Note: == in Python is like .equals in Java
            print('File accepted.')
        else:
            print('Unexpected response:', response)

        num_lines = int(input('Enter the number of lines you want to send (0 to exit):'))

    tcp_socket.sendall(b'\x00\x00')
    time.sleep(1)  # Just to mess with your servers. :-)  Your code should work with this line here.
    tcp_socket.sendall(b'\x00\x00')
    response = tcp_socket.recv(1)
    # print(response)
    if response == b'Q':  # Reminder: == in Python is like .equals in Java
        print('Server closing connection, as expected.')
    else:
        print('Unexpected response:', response)

    tcp_socket.close()


def tcp_receive(listen_port):
    """
    - Listen for a TCP connection on a designated "listening" port
    - Accept the connection, creating a connection socket
    - Print the address and port of the sender
    - Repeat until a zero-length message is received:
      - Receive a message, saving it to a text-file (1.txt for first file, 2.txt for second file, etc.)
      - Send a single-character response 'A' to indicate that the upload was accepted.
    - Send a 'Q' to indicate a zero-length message was received.
    - Close data connection.
   
    :param int listen_port: Port number on the server to listen on

    -Author Josh Sopa
    """

    print('tcp_receive (server): listen_port={0}'.format(listen_port))
    # create server to listen
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind((LISTEN_ON_INTERFACE, listen_port))
    # listening
    listen_socket.listen(1)
    (data_socket, sender_address) = listen_socket.accept()

    parse_bytes(data_socket)

    data_socket.close()
    listen_socket.close()


def parse_bytes(data_socket):
    """
    Parses the bytes after recieving a message
    :param data_socket: the data socket to read bytes off of
    Author- Josh sopa
    """
    accept_decline = b'A'
    message_number = 0
    while accept_decline == b'A':

        # get number of lines
        data = next_byte(data_socket)
        for lines in range(0, 3):
            data += next_byte(data_socket)
        num_lines = int.from_bytes(data, 'big')

        # Size of message > 0
        if int.from_bytes(data, 'big') > 0:
            message_data = b''
            message_number += 1
            # get message data and stor in message_data
            line = 0
            while line < num_lines:
                data = next_byte(data_socket)
                if data == b'\n':
                    line += 1
                message_data += data

            print(message_data)
            create_file(message_data, message_number)
            # accept another message
            accept_decline = b'A'
        else:
            # closing socket
            accept_decline = b'Q'

        # talk back to server
        data_socket.sendall(accept_decline)


def create_file(message, number):
    """
    Create a text file given a bytes and int parameter
    :param message: The message in bytes that is being put in a text file
    :param number: The number to be assigned the name of the text file
    -Author Hudson Arney
    """
    number = str(number)
    text_file = open(number+".txt", "wb")
    text_file.write(message)
    text_file.close()


def next_byte(data_socket):
    """
    Read the next byte from the socket data_socket.
   
    Read the next byte from the sender, received over the network.
    If the byte has not yet arrived, this method blocks (waits)
      until the byte arrives.
    If the sender is done sending and is waiting for your response, this method blocks indefinitely.
   
    :param data_socket: The socket to read from. The data_socket argument should be an open tcp
                        data connection (either a client socket or a server data socket), not a tcp
                        server's listening socket.
    :return: the next byte, as a bytes object with a single byte in it
    """
    return data_socket.recv(1)


# Invoke the main method to run the program.
main()
