#!/usr/bin/env python3

import argparse
import socket
import selectors
import traceback

import lib.libserver as libserver

sel = selectors.DefaultSelector()

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    message = libserver.Message(sel, conn, addr)
    sel.register(conn, selectors.EVENT_READ, data=message)


def parse_arguments():
    parser = argparse.ArgumentParser(prog="app-server",
        description="Basic socket server which connect to the destinated host (send an empty string to accept every ip) in the desired port",
        epilog="Finished runtime")

    parser.add_argument("host", nargs="?", type=str, help="IP Adress where the socket will be created")
    parser.add_argument("port", nargs="?", type=int, help="Port in which the socket will be allocated")
    parser.add_argument("-e", "--especify", action="store_true", help="Says if the host and port must be especified")
    
    args = parser.parse_args()
    test_errors(parser, args)
    
    return args

def test_errors(parser, args):
    if args.especify:
        if args.host == None:
            code_error = 1
            parser.exit(code_error, message="Code error %i: Host not especified\n" % code_error)
        if args.port == None:
            code_error = 2
            parser.exit(code_error,message="Code error %i: Port not especified\n" % code_error)

def set_arguments(args):
    if args.especify == False:
        return "", 65432        
    return args.host, args.port

def main():
    args = parse_arguments()
    host, port = set_arguments(args)
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Avoid bind() exception: OSError: [Errno 48] Address already in use
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind((host, port))
    lsock.listen()
    print(f"Listening on {(host, port)}")
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

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

if __name__ == "__main__":
    main()
