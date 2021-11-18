#!/usr/bin/env python3

"""Provide simple status of the logger."""
import json
import logging
from dataclasses import dataclass
from datetime import datetime as dt
from datetime import timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread


@dataclass
class Data:
    """Class to ensure format of the data."""

    last_rx_time: dt
    max_delta: timedelta
    data_dict: dict

    @property
    def valid(self) -> bool:
        """Return validty, i.e. younger than the max_delta."""
        return (self.last_rx_time - dt.now()) < self.max_delta


def get_server(data: Data):
    """Closure for data."""

    class Server(BaseHTTPRequestHandler):
        """Simple webserver that serves the data dict from the closure as json."""

        # overwriting methods, names are given
        # pylint: disable=invalid-name

        def _set_headers(self):
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

        def do_HEAD(self):
            """Set header to SUCCESS and application/json."""
            self._set_headers()

        def do_GET(self):
            """Serve the data tuple."""
            # pylint: disable=broad-except
            data_clean = {}
            all_good = True

            # Make objects serializiable
            try:
                for key, val in data.data_dict.items():
                    data_clean[key] = str(val)
            except Exception as err:
                all_good &= False
                logging.warning("Error: %s", err)

            # Dump it to json
            try:
                data_clean["all_good"] = all_good & data.valid
                data_json = json.dumps(data_clean, ensure_ascii=False)
                # Set header and body
                self._set_headers()
                self.wfile.write(data_json.encode("utf-8"))
                # Debug message
                logging.debug("Data reply: %s", data_json)
            except Exception as err:
                logging.warning("Error: %s", err)

        def log_request(*args, **kwargs):
            """Only log requests as logging.debug."""
            # No method, overriding an inherited method
            # pylint: disable=no-method-argument
            logging.debug("Successfull request.")
            logging.debug("\targs: %s", args)
            logging.debug("\t:kwargs %s", kwargs)

    return Server


class StatusServer:
    """Simple status server. Serving the current status as dict."""

    def __init__(self, data: Data, port: int = 8080):
        """Initialize the server.

        Parameters
        ----------
        data : Data
            Dataclass to transport payload

        port : int
            Port of the server, defaults to 8080

        """
        self.port = port
        assert isinstance(data, Data)
        self.data = data

    def run(self):
        """Serve the Server."""
        server_address = ("", self.port)
        server = get_server(data=self.data)
        httpd = HTTPServer(server_address, server)

        logging.info("Starting httpd on port %i...", self.port)
        httpd.serve_forever()


def main():
    """Run the server for eternity.

    Start the server as it's own thread and run it.
    """
    server = StatusServer(port=8000, data={"time": dt.now().timestamp()})
    thread = Thread(target=server.run)
    thread.start()
    logging.info("Server has been kicked off.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
