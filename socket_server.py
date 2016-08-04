
import socket, select
import signal

class SimpleSignalHandler:
  should_exit = False

  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self,signum, frame):
    self.should_exit = True


class Client:
    addr = None

    def __init__(self, addr):
        self.addr = addr


class Server:
    active_sockets = []
    clients_info = {}
    is_running = False

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def start(self, max_clients=10):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(max_clients)
        self.active_sockets.append(self.server_socket)
        self.is_running = True

    def shutdown(self):
        for sock in self.active_sockets:
            sock.close()

        # clear all connections list
        self.active_sockets[:] = []
        self.clients_info.clear()

        # close listening socket
        self.server_socket.close()

        self.is_running = False

    def disconnect_client(self, sockfd):
        sockfd.close()
        self.active_sockets.remove(sockfd)
        client = self.clients_info.pop(sockfd)
        print "Client (%s, %s) is offline" % client.addr

    def select(self, timeout=1):
        try:
            # get the list of sockets which are ready to be read
            read_sockets,write_sockets,error_sockets = select.select(self.active_sockets,[] , self.active_sockets, timeout)

            for sock in read_sockets:

                # new connection
                if sock == self.server_socket:
                    # Handle the case in which there is a new connection recieved through server_socket
                    sockfd, addr = self.server_socket.accept()
                    self.active_sockets.append(sockfd)
                    self.clients_info[sockfd] = Client(addr)
                    print "Client (%s, %s) connected" % addr

                # got message from a client
                else:
                    # in Windows, when a TCP program closes abruptly,
                    # a "Connection reset by peer" exception will be thrown
                    try:
                        data = sock.recv(RECV_BUFFER)

                        # if client socket has been closed - the received buffer will be empty
                        if len(data) > 0:
                            # echo back the client message
                            sock.send(data)
                        else:
                            # client disconnected
                            self.disconnect_client(sock)

                    # client disconnected (Windows)
                    except:
                        self.disconnect_client(sock)
                        continue

            for sock in error_sockets:
                self.disconnect_client(sock)

        except (select.error, KeyboardInterrupt) as e:
            self.shutdown()


if __name__ == "__main__":

    RECV_BUFFER = 1024      # buffer size
    PORT = 8000
    MAX_CLIENTS = 10

    signal_handler = SimpleSignalHandler()

    server = Server("0.0.0.0", PORT)
    server.start(MAX_CLIENTS)
    print "Server started on port " + str(PORT)

    timeout = 1
    while server.is_running:
        server.select(timeout)
        if signal_handler.should_exit:
            server.shutdown()

    print "Server exited"

