#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback

import libserver

sel = selectors.DefaultSelector()


def check_args(args):
    """
    Check arguments that we receive asd  input of the program.
    If not valid, the program ends.
    """
    if len(args) != 3:
        print(f"Usage: {args[0]} <host> <port>")
        sys.exit(1)

#TODO: check server not responding to request
def set_up_connection(host, port):
    """
    Sets up the server to wait for a client.
    Host and port args are received via command line args.
    """
    host, port = host, int(port)
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Avoid bind() exception: OSError: [Errno 48] Address already in use
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind((host, port))
    lsock.listen()
    print(f"Listening on {(host, port)}")
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

def accept_wrapper(sock):
    """
    Defines the behavior when a connection has been established with a client.
    """
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    message = libserver.Message(sel, conn, addr)
    sel.register(conn, selectors.EVENT_READ, data=message)


# Program start
check_args(sys.argv)
set_up_connection(sys.argv[1], sys.argv[2])

#Loop that wait for a client
try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                message = key.data
                try:
                    message.process_events(mask)
                except Exception:
                    print(
                        f"Main: Error: Exception for {message.addr}:\n"
                        f"{traceback.format_exc()}"
                    )
                    message.close()
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()
