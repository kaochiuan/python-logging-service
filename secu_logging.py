#!/usr/bin/env python3
import pickle
import logging
import logging.handlers
import socketserver
import socket
import struct
from logging.handlers import RotatingFileHandler


class LogRecordStreamHandler(socketserver.StreamRequestHandler):
    """Handler for a streaming logging request.

    This basically logs the record using whatever logging policy is
    configured locally.
    """
    logging.basicConfig(level=logging.INFO, format='%(relativeCreated)6d %(process)d %(message)s')
    logger = logging.getLogger(__name__)
    if logger.hasHandlers():
        for handler in logger.handlers:
            logger.removeHandler(handler)

    fh = RotatingFileHandler(filename="/opt/daemon/service/secu_logging.log", maxBytes=1024 * 5, backupCount=7)
    logger.addHandler(fh)

    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        while 1:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack(">L", chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self.un_pickle(chunk)
            record = logging.makeLogRecord(obj)
            self.handle_log_record(record)

    def un_pickle(self, data):
        return pickle.loads(data)

    def handle_log_record(self, record):
        self.logger.handle(record)


class LogRecordSocketReceiver(socketserver.TCPServer):
    """simple TCP socket-based logging receiver suitable for testing.
    """
    SYSTEMD_FIRST_SOCKET_FD = 3
    allow_reuse_address = 1

    def __init__(self, host='localhost',
                 port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
                 handler=LogRecordStreamHandler):
        socketserver.TCPServer.__init__(self, (host, port), handler, bind_and_activate=False)
        self.socket = socket.fromfd(self.SYSTEMD_FIRST_SOCKET_FD, self.address_family, self.socket_type)
        self.abort = 0
        self.timeout = 1
        self.log_name = None

    def serve_until_stopped(self):
        import select
        abort = 0
        while not abort:
            rd, wr, ex = select.select([self.socket.fileno()],
                                       [], [],
                                       self.timeout)
            if rd:
                self.handle_request()
            abort = self.abort


def main():
    # logging.basicConfig(
    #     format="%(relativeCreated)5d %(name)-15s %(levelname)-8s %(message)s")
    tcp_server = LogRecordSocketReceiver()
    print("About to start TCP server...")
    tcp_server.serve_until_stopped()


if __name__ == "__main__":
    main()
