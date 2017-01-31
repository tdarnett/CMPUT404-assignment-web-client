#!/usr/bin/env python
# coding: utf-8
#
# Copyright 2017 Taylor Arnett
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    # compile the url parsing regular expression once.
    pattern = re.compile(r"(https?:\/\/)?([^:/]*)(:(\d*))?(.*)?") # inspired by aktagon (Creative Commons Attribution 3.0 License) https://snippets.aktagon.com/snippets/72-split-a-url-into-protocol-domain-port-and-uri-using-regular-expressions

    def connect(self, host, port):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        return client

    def get_code(self, data):
        return int(data.split('\r\n\r\n')[0].split('\r\n')[0].split(' ')[1])

    def get_headers(self,data):
        return data.split('\r\n\r\n')[0]

    def get_body(self, data):
        return data.split('\r\n\r\n')[1]

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        url_contents = self.parse_url(url)
        request = 'GET %s HTTP/1.1\r\n' % url_contents.get('path')
        request += 'Host: %s\r\n' % url_contents.get('host')
        request += 'Connection: close\r\n'
        request += 'Accept: %s\r\n\r\n' % '*/*'

        client = self.connect(url_contents.get('host'), int(url_contents.get('port')))
        client.sendall(request)

        response = self.recvall(client)
        code = self.get_code(response)
        body = self.get_body(response)

        print response
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        content_length = 0
        payload = ''
        if args:
            payload = urllib.urlencode(args)
            content_length = len(payload)

        url_contents = self.parse_url(url)
        request = 'POST %s HTTP/1.1\r\n' % url_contents.get('path')
        request += 'Host: %s\r\n' % url_contents.get('host')
        request += 'Connection: close\r\n'
        request += 'Accept: %s\r\n' % '*/*'
        request += 'Content-Type: application/x-www-form-urlencoded\r\n'
        request += 'Content-Length: %s\r\n\r\n' % content_length
        request += payload + '\r\n\r\n'

        client = self.connect(url_contents.get('host'), int(url_contents.get('port')))
        client.sendall(request)

        response = self.recvall(client)

        code = self.get_code(response)
        body = self.get_body(response)

        print response
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

    def parse_url(self, url):
        """
        given a url, this will parse the host, port and path sections using regular expressions
        :param url: string of the full url to be parsed
        :return: dict containing the host, port and path
        """
        contents = dict(
            host=None,
            port=None,
            path=None,
        )

        result = self.pattern.match(url)

        contents['host'] = result.group(2)
        contents['port'] = result.group(4) or 80
        contents['path'] = result.group(5) or '/'

        return contents


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )
