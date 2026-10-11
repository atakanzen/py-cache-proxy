# py-cache-proxy

A proxy server for caching HTTP responses from a given origin upstream URL, implemented with Python standard libraries only.

## Supported CLI options:

- `--port`: The port that the proxy server will run on localhost.
- `--origin`: The origin URL for the upstream server that we want to cache its responses with our proxy server.
- `--clear-cache`: Clears out the local `.cache` folder.

