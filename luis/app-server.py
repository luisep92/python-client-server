import socket
import selectors
import traceback
import argparse

import libserver

sel = selectors.DefaultSelector()


def parse_args():
    """
    Parse arguments received via command line
    If not valid, the program ends.
    """
    parser = argparse.ArgumentParser(
        prog="socket-server",
        description=
        """
            Server in python that receives json object an validate them against schema. 
            Without arguments, socket will be 0.0.0.0:65432
        """
    )
    parser.add_argument("host", nargs="?", default="", help="IP of the socket where the server will listen. "
                                                            "Entry an empty string to listen in all available IPs.")
    parser.add_argument("port", nargs="?", default=65432, help="Port of the socket where the server will listen")
    parser.add_argument("-e", "--example", action="store_true", help="Shows an example line which you can use to run the program")
    args = parser.parse_args()
    if args.example:
        parser.exit('Example: python3 app-server.py "" 65432')
    return args


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


def try_process_connection(key, mask):
    """
    Accepts the connection with the client and proccess read and write events
    """
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


def main():
    args = parse_args()
    set_up_connection(args.host, args.port)

    # Loop that wait for a client
    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                try_process_connection(key, mask)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        sel.close()


# Program start
if __name__ == "__main__":
    main()
