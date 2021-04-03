#!/usr/bin/python3

import socket
from http.server import BaseHTTPRequestHandler, HTTPServer

import urllib.parse as urlparse
from urllib.parse import parse_qs

import logging

# create logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter("[%(asctime)s] %(message)s")

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


hostName = "0.0.0.0"
hostPort = 8081


class MyServer(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    # GET is for clients geting the predi
    def do_GET(self):
        self._set_headers()
        self.wfile.write(f"ack".encode())

        url = f"http://a.com{self.path}"
        parsed = urlparse.urlparse(url)

        query = parse_qs(parsed.query)

        if "text" in query and "title" in query:
            logger.info(f"{''.join(query['title'])} - {''.join(query['text'])}")


myServer = HTTPServer((hostName, hostPort), MyServer)
logger.info(f"Started notification server on {hostName}:{hostPort}")

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

myServer.server_close()
logger.info(f"Server stopped")
