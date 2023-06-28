#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback
import json

import libclient

sel = selectors.DefaultSelector()


def create_request(obj):
    """
    Creates a  request that is sent to the server.
    Receives an object as parameter, that is created from our json file.
    """
    return dict(
        type="text/json",
        encoding="utf-8",
        content=obj
    )


def check_args(args):
    """
    Checks if arguments are correct to start the program
    If correct, return the object that we send. If not, program ends.
    """
    if len(args) != 4:
        print(f"Usage: {args[0]} <host> <port> <json>")
        sys.exit(1)
    obj = libclient.is_valid_file(args[3])
    if obj == False:
        print(f"File {args[3]} is not a valid json")
        sys.exit(1)
    return obj


def start_connection(host, port, request):
    """
    Starts a connection with the server.
    Receives the socket where is working the server and the request that we will send
    """
    addr = (host, port)
    print(f"Starting connection to {addr}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = libclient.Message(sel, sock, addr, request)
    sel.register(sock, events, data=message)

# Set up client
item = check_args(sys.argv)
host, port = sys.argv[1], int(sys.argv[2])
request = create_request(item)
start_connection(host, port, request)

# Connection loop
try:
    while True:
        events = sel.select(timeout=1)
        for key, mask in events:
            message = key.data
            try:
                message.process_events(mask)
            except Exception:
                print(
                    f"Main: Error: Exception for {message.addr}:\n"
                    f"{traceback.format_exc()}"
                )
                message.close()
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()
