import argparse
import socket
import selectors
import traceback
import libclient

# This reference needs to exist before we declare the functions
sel = selectors.DefaultSelector()
default_host = "127.0.0.1"
default_port = 65432

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


def parse_args():
    """
    Parse arguments received via command line
    If not valid, the program ends.
    """
    parser = argparse.ArgumentParser(
        prog="app-client",
        description="Client that sends json objects to a server of validation.\n "
                    "If socket is not defined, it uses 127.0.0.1:65432\n"
                    "Example of usage: python3 app-client.py 127.0.0.1 65432 user.json"
    )
    parser.add_argument("host", nargs="?", help="IP where the ser is listening. Default 127.0.0.1", default=default_host)
    parser.add_argument("port", nargs="?", help="port where the server is listening. Default 65432", default=default_port)
    parser.add_argument("file", help="name of the json")
    args = parser.parse_args()
    obj = libclient.is_valid_file(args.file)
    if not obj:
        parser.exit(f"File {args.file} is not a valid json")
    return obj, args


def try_process_events(events):
    for key, mask in events:
        message = key.data
        try:
            message.process_events(mask)
        except TypeError:
            print(
                f"Main: Error: Exception for {message.addr}:\n"
                f"{traceback.format_exc()}"
            )
            message.close()


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


def main():
    # Set up client
    item, args = parse_args()
    host, port = args.host, int(args.port)
    request = create_request(item)
    start_connection(host, port, request)

    # Connection loop
    try:
        while True:
            events = sel.select(timeout=1)
            try_process_events(events)
            # Check for a socket being monitored to continue.
            if not sel.get_map():
                break
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        sel.close()


# Program start
if __name__ == "__main__":
    main()
