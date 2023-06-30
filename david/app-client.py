#!/usr/bin/env python3

import argparse
import socket
import selectors
import traceback
import json

import libclient

sel = selectors.DefaultSelector()

def load_json_file(data_file):
    try:
        with open(data_file) as file:
            read = file.read()
            return json.loads(read)
    except Exception:
        argparse.ArgumentParser().exit(f"File {data_file} could not been loaded")

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



"""
Command created for debugging
"""
# test_command = ["", "127.0.0.1", "65432", "Pepe.json"]
# host, port = test_command[1], int(test_command[2])
# json_file_name = test_command[3]

defaults = {"port":65432, "host": "127.0.0.1"}

def set_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("host", nargs="?", type=str, help="IP Adress where the socket will be created")
    parser.add_argument("port", nargs="?", type=int, help="Port in which the socket will be allocated")
    parser.add_argument("file", nargs=1, type=str, help="JSON file which will be examined")
    parser.add_argument("-e", "--especify", action="store_true", help="Says if the host and port must be especified")
    
    args = parser.parse_args()

    if not args.especify:
        args.port = defaults["port"]
        args.host = defaults["host"]

    if args.especify:
        if args.host == None:
            code_error = 1
            parser.exit(code_error, f"Code Error: {code_error}, Host not especified")
        if args.port == None:
            code_error = 2
            parser.exit(code_error, f"Code Error: {code_error}, Port not especified")
    return args


def main():
    args = set_arguments()
    host, port = args.host, args.port
    json_file_name = args.file[0]

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