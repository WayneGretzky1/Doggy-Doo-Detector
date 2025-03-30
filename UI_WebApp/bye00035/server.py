#!/usr/bin/env python3

import socket
import os
import stat
from urllib.parse import unquote_plus
from argparse import ArgumentParser
from threading import Thread

# Equivalent to CRLF, named NEWLINE for clarity
NEWLINE = "\r\n"


# Let's define some functions to help us deal with files, since reading them
# and returning their data is going to be a very common operation.

def get_file_contents(file_name):
    """Returns the text content of `file_name`"""
    with open(file_name, "r") as f:
        return f.read()


def get_file_binary_contents(file_name):
    """Returns the binary content of `file_name`"""
    with open(file_name, "rb") as f:
        return f.read()


def has_permission_other(file_name):
    """Returns `True` if the `file_name` has read permission on other group

    In Unix based architectures, permissions are divided into three groups:

    1. Owner
    2. Group
    3. Other

    When someone requests a file, we want to verify that we've allowed
    non-owners (and non group) people to read it before sending the data over.
    """
    stmode = os.stat(file_name).st_mode
    return getattr(stat, "S_IROTH") & stmode > 0


# Some files should be read in plain text, whereas others should be read
# as binary. To maintain a mapping from file types to their expected form, we
# have a `set` that maintains membership of file extensions expected in binary.
# We've defined a starting point for this set, which you may add to as
# necessary.
# TODO: Finish this set with all relevant files types that should be read in
# binary
binary_type_files = set(["jpg", "jpeg", "png", "mp3"])


def should_return_binary(file_extension):
    """
    Returns `True` if the file with `file_extension` should be sent back as
    binary.
    """

    return file_extension in binary_type_files


# For a client to know what sort of file you're returning, it must have what's
# called a MIME type. We will maintain a `dictionary` mapping file extensions
# to their MIME type so that we may easily access the correct type when
# responding to requests.
# TODO: Finish this dictionary with all required MIME types
mime_types = {
    "html": "text/html",
    "css": "text/css",
    "js": "application/javascript",
    "jpg": "image/jpg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "mp3": "audio/mpeg"
}


def get_file_mime_type(file_extension):
    """
    Returns the MIME type for `file_extension` if present, otherwise
    returns the MIME type for plain text.
    """
    mime_type = mime_types[file_extension]
    return mime_type if mime_type is not None else "text/plain"


class HTTPServer:
    """
    Our actual HTTP server which will service GET and POST requests.
    """

    def __init__(self, host="localhost", port=4131, directory="."):
        print(f"Server started. Listening at http://{host}:{port}/")
        self.host = host
        self.port = port
        self.working_dir = directory

        self.setup_socket()
        self.accept()

        self.teardown_socket()

    def setup_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(128)

    def teardown_socket(self):
        if self.sock is not None:
            self.sock.shutdown()
            self.sock.close()

    def accept(self):
        while True:
            (client, address) = self.sock.accept()
            th = Thread(target=self.accept_request, args=(client, address))
            th.start()

    def accept_request(self, client_sock, client_addr):
        data = client_sock.recv(4096)
        req = data.decode("utf-8")


        response = self.process_response(req)
        client_sock.send(response)

        # clean up
        client_sock.shutdown(1)
        client_sock.close()

    def process_response(self, request):
        formatted_data = request.strip().split(NEWLINE)
        request_words = formatted_data[0].split()

        if len(request_words) == 0:
            return

        requested_file = request_words[1][1:]
        if request_words[0] == "GET":
            return self.get_request(requested_file, formatted_data)
        if request_words[0] == "POST":
            return self.post_request(requested_file, formatted_data)
        if request_words[0] == "HEAD":
            return self.get_request(requested_file, formatted_data)
        return self.method_not_allowed()

    
    def head_request(self, requested_file, data) -> bytes:
        requested_file = os.path.join('.', requested_file)
        print("\nRequested File: ",requested_file)
        
        if not os.path.exists(requested_file):
            ret = self.resource_not_found()
        elif not has_permission_other(requested_file):
            ret = self.resource_forbidden()
        else:
            # Use MIME to determine file extension
            file_extension = requested_file.split(".")[-1]
            content_type = get_file_mime_type(file_extension)

            # Only return header
            header ='HTTP/1.1 200 OK\n'
            header += 'Content-Type: ' + content_type + '\n'
            header += 'Connection: close\n\n'
            ret = header
        
        return ret.encode("UTF-8")
    

    # TODO: Write the response to a GET request
    def get_request(self, requested_file, data) -> bytes:
        """
        Responds to a GET request with the associated bytes.

        If the request is to a file that does not exist, returns
        a `NOT FOUND` error.

        If the request is to a file that does not have the `other`
        read permission, returns a `FORBIDDEN` error.

        Otherwise, we must read the requested file's content, either
        in binary or text depending on `should_return_binary` and
        send it back with a status set and appropriate mime type
        depending on `get_file_mime_type`.
        """

        requested_file = os.path.join('.', requested_file)
        print("\nRequested File: ", requested_file)
        
        # Used for redirect to youtube
        redirect_check = requested_file.split('?')[0]
        
        if redirect_check == r'.\redirect':
            search_terms = requested_file.split('=')[1]
            location = "https://www.youtube.com/results?search_query="
            location += search_terms.replace(" ", "+")

            # Build the header
            header ='HTTP/1.1 307 Temporary Redirect\n'
            header += 'Location: ' + location + '\n'
            header += 'Connection: close\n\n'
            ret = header
        elif not os.path.exists(requested_file):
            ret = self.resource_not_found()
        elif not has_permission_other(requested_file):
            ret = self.resource_forbidden()
        else:
            # Use MIME to determine file extension
            file_extension = requested_file.split(".")[-1]
            content_type = get_file_mime_type(file_extension)
            # Build the header
            header ='HTTP/1.1 200 OK\n'
            header += 'Content-Type: ' + content_type + '\n'
            header += 'Connection: close\n\n'
            
            # Depending on content type, either get contents in binary or text
            if should_return_binary(file_extension):
                ret = header.encode("UTF-8") + get_file_binary_contents(requested_file)
                return ret
            else:
                ret = header + get_file_contents(requested_file)
            
        return ret.encode("UTF-8")
        

    # TODO: Write the response to a POST request
    def post_request(self, requested_file: str, data: list) -> bytes:
        """
        Responds to a POST request with an HTML page containing a table
        where each row corresponds to the field name, and field value from
        the "myform.html" form submission.

        A post request through the form will send over key value pairs
        through "x-www-form-urlencoded" format. You may learn more about
        that here:
          https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST
        You /do not/ need to check the POST request's Content-Type to
        verify the encoding used (although a real server would).

        Care should be taken in forming values with spaces. Since the request
        was urlencoded, it will need to be decoded using
        `urllib.parse.unquote` or `urllib.parse.unquote_plus`.

        Note: When the "myform.html" form is submitted with each field 
        filled, each row should contain a name and value, however, since 
        this function responds to each POST request, it's possible that 
        the contents of the POST request don't conform to what your form is 
        set to submit. In that case, you should ignore additional fields, 
        and also gracefully handle missing fields. 
        """
        print("req", requested_file)
        print("data", data)

        events = get_body_params(data[-1])
        print("events", events)


        header ='HTTP/1.1 200 OK\n'
        header += 'Connection: close\n\n'
        
        event_log = (
            """
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title> Event Submission </title>
                <link rel="stylesheet" type="text/css" href="/static/css/style.css">
            </head>
            <body>
                <div class="flex-container">
                    <div><a href="/static/html/myschedule.html">My Schedule</a></div>
                    <div><a href="/static/html/myform.html">Form Input</a></div>
                    <div><a href="/static/html/aboutme.html">About Me</a></div>
                    <div><a href="/static/html/stocks.html">About Me</a></div>
                </div>
                <h1> My New Events </h1>
                <div class="event-form">
                    <table>
                        """
            + submission_to_table(events)
            + """
                    </table>
                </div>
            </body>
            </html>""",
            "text/html; charset=utf-8",
        )
        ret = header + ''.join(event_log)

        return ret.encode("UTF-8")
        

    def method_not_allowed(self) -> bytes:
        """
        Returns 405 not allowed status and gives allowed methods.

        
        """
        message = f"HTTP/1.1 405 METHOD NOT ALLOWED" \
            + NEWLINE + NEWLINE.join(["Allow: GET,POST", "Connection: close"]) \
            + NEWLINE + NEWLINE 
        
        return message.encode("utf-8")

    # TODO: Make a function that handles not found error
    def resource_not_found(self) -> bytes:
        """
        Returns 404 not found status and sends back our 404.html page.
        """
        html_content = get_file_contents(r"./static/html/404.html")
        header = 'HTTP/1.1 404 Not Found\n'
        header += 'Content-Type: text/html\n'
        header += 'Connection: close\n\n'
        ret = header + html_content

        return ret
        

    # TODO: Make a function that handles forbidden error
    def resource_forbidden(self) -> bytes:
        """
        Returns 403 FORBIDDEN status and sends back our 403.html page.
        """
        html_content = get_file_contents(r"./static/html/403.html")
        header = 'HTTP/1.1 404 Not Found\n'
        header += 'Content-Type: text/html\n'
        header += 'Connection: close\n\n'
        ret = header + html_content

        return ret

def get_body_params(body):
    if not body:
        return {}
    parameters = body.split("&")

    # split each parameter into a (key, value) pair, and escape both
    def split_parameter(parameter):
        k, v = parameter.split("=", 1)
        k_escaped = unquote_plus(k)
        v_escaped = unquote_plus(v)
        return k_escaped, v_escaped

    body_dict = dict(map(split_parameter, parameters))
    print(f"Parsed parameters as: {body_dict}")
    # return a dictionary of the parameters
    return body_dict


def submission_to_table(item):
    # """TODO: Takes a dictionary of form parameters and returns an HTML table row
    #    The HTML row will be in the same format as a row on your schedule

    # An example input dictionary might look like: 
    # {
    #  'event': 'Sleep',
    #  'day': 'Sun',
    #  'start': '01:00',
    #  'end': '11:00', 
    #  'phone': '1234567890', 
    #  'location': 'Home',
    #  'url': 'https://example.com'
    # }
    # """

    return (
    """
    <tr >
        <td> Event </td>
        <td>
         """ + item['event'] +
         """</td>
    <tr >

    <tr >
        <td> Day </td>
        <td>
         """ + item['day'] + 
         """</td>
    <tr >

    <tr >
        <td> Start </td>
        <td>
         """ + item['start'] + 
         """</td>
    <tr >

    <tr >
        <td> End </td>
        <td>
         """ + item['end'] + 
         """</td>
    <tr >

    <tr >
        <td> Phone </td>
        <td>
         """ + item['phone'] + 
         """</td>
    <tr >

    <tr >
        <td> Location </td>
        <td>
         """ + item['location'] + 
         """</td>
    <tr >

    <tr >
        <td> URL </td>
        <td>
         """ + item['url'] + 
         """</td>
    </tr>
    """
    )


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('port', type=int, nargs='?', default=4131,
                        help='specify a port to operate on (default: 4131)')

    args = parser.parse_args()
    return args.port

if __name__ == "__main__":
    port = parse_args()
    HTTPServer("localhost", port)
