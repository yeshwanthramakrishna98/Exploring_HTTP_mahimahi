#!/usr/bin/env python
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import BaseHTTPServer
#import SimpleHTTPServer
import SocketServer
import base64
import urllib
import sys
import subprocess
import time
import socket
import ssl
import uuid
import os
import atexit

def parse_header(x):
    pieces = x.split(":")
    head = pieces[0]
    val = pieces[1]
    for i in range(2, len(pieces)):
        val = val + ":" + pieces[i]
    if val[0] == " ":
        val = val[1:]
    return [head, val]

#could use ForkingMixIn to spawn another process rather than another thread (or ThreadingMixIn)
class ThreadingSimpleServer(SocketServer.ForkingMixIn,
                            BaseHTTPServer.HTTPServer):
    pass

class Request_Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    def do_GET(self):
        command = "findmatch " + dir_to_use + " \"" + self.requestline + "\""
        proc = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
        (out,err) = proc.communicate()
        self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.wfile.write(out)
        # check if server wants to close connection, if yes- close it
        y = out.split("\r\n")
        for x in range(1, len(y)-1):
            if ( y[x] == '' ):
                break
            res = parse_header(y[x])
            if ( res[0].lower() == "connection" ):
                if ( res[1].lower() == "close" ):
                    self.close_connection = 1
                else:
                    self.connection.settimeout(5)
                #elif ( res[1].lower() == "keep-alive" ):
                #    self.close_connection = 0
        return

    def do_POST(self):
        command = "findmatch " + dir_to_use + " \"" + self.requestline + "\""
        proc = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
        (out,err) = proc.communicate()
        self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.wfile.write(out)
        # check if server wants to close connection, if yes- close it
        y = out.split("\r\n")
        for x in range(1, len(y)-1):
            if ( y[x] == '' ):
                break
            res = parse_header(y[x])
            if ( res[0].lower() == "connection" ):
                if ( res[1].lower() == "close" ):
                    self.close_connection = 1
                else:
                    self.connection.settimeout(5)
                #elif ( res[1].lower() == "keep-alive" ):
                #    self.close_connection = 0

    def log_message(self, format, *args):
        return

    def exit_handler():
        os.system("sudo rm -rf /home/ravi/mahimahi/certificates")
        os.system("mkdir /home/ravi/mahimahi/certificates")
    atexit.register(exit_handler)

def run(ip, port, server_class=HTTPServer, handler_class=Request_Handler):
    server_address = (ip, port)
    httpd = ThreadingSimpleServer(server_address, handler_class)
    #httpd = server_class(server_address, handler_class)
    if ( port == 443 ):
        httpd.socket = ssl.wrap_socket(httpd.socket, certfile=cert_path, server_side=True, keyfile='/home/ravi/ssl-cert.key')
        print "here"
    print 'Listening on port ' + str(port)
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv
    if len(argv) == 5:
        global dir_to_use
        dir_to_use = argv[4]
        global cert_path
        domain = argv[3]
        unique = str(uuid.uuid4())
        cert_path = "/home/ravi/mahimahi/certificates/" + unique + ".crt"
        csr_path = "/home/ravi/mahimahi/certificates/" + unique + ".csr"
        os.system("openssl req -new -key /home/ravi/ssl-cert.key -out " + csr_path + " -subj /CN=" + domain)
        os.system("openssl x509 -req -in " + csr_path + " -CA /home/ravi/rootCA.crt -CAkey /home/ravi/rootCA.key -CAcreateserial -out " + cert_path + " -days 500")
        run(ip=argv[1], port=int(argv[2]))
    else:
        print "ERROR"
