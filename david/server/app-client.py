#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback
import json
import re

from lib import libclient

sel = selectors.DefaultSelector()

def load_json_file(data_file):
    try:
        with open(data_file) as file:
            read = file.read()
            return json.loads(read)
    except Exception:
        print(f"File {data_file} could not been loaded")
        sys.exit(1)

def create_request(data_file: str):
    content = load_json_file(data_file)
    return dict(
        type="text/json",
        encoding="utf-8",
        content = content
    )

def start_connection(host, port, request):
    addr = (host, port)
    print(f"Starting connection to {addr}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = libclient.Message(sel, sock, addr, request)
    sel.register(sock, events, data=message)


if len(sys.argv) != 4:
    print(f"Usage: {sys.argv[0]} <host> <port> <json>")
    sys.exit(1)

if not re.compile(".*\.json").match(str(sys.argv[3])):
    print("Non-json aren't accepted")
    sys.exit(1)


"""
Command created for debbugging
"""
# test_command = ["", "127.0.0.1", "65432", "Pepe.json"]
# host, port = test_command[1], int(test_command[2])
# json_file_name = test_command[3]


def main():
    host, port = sys.argv[1], int(sys.argv[2])
    json_file_name = sys.argv[3]

    request = create_request(json_file_name)
    start_connection(host, port, request)

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


if __name__ == "__main__":
    main()