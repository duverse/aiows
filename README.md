AIOHttp WebSockets Server
-------------------------

Easy and ready to use websocket server based on AIOHTTP framework. This tool allows you
to easily build application based on websockets in a short time.

Requirements
------------

 - Python 3.6+

AIOWS Does not requires anything else. It's a really simple and lightweight application
which can give you ability to communicate your server with the clients in a real-time.

AIOWS Supports three types of packages:

 - JSON
 - Text
 - Bytes
 
This allows you to build whatever you want. For example - video chat, multiplayer game,
chat, notifications...

Installation
------------

    pip install aiows
    
After installation - you can start to develop your application. Example of the front-end
sockets usage you can see at **demo/simple-socket.js**.

Usage
-----

**Basic understanding**

AIOWS Does not supports WebSockets bidirectional communication. It means that you'll not
be able to send packets to the server via sockets. It's done for security and stability
reasons. Instead of bidirectional communication, AIOWS has HTTP API which allows you to
share packages between WS Subscribers.

HTTP API Is open from global network, so for security reasons you can setup publish password
which will filter any unauthorized requests.

**AIOWS**

    $ aiows --help
    usage: aiows [-h] [--pwd PWD] [--usock USOCK] [--host HOST] [--port PORT]
                 [--reuse-addr REUSE_ADDR] [--reuse-port REUSE_PORT]
                 [--url-prefix URL_PREFIX]
    
    AIOHttp WebSocket server
    
    optional arguments:
      -h, --help            show this help message and exit
      --pwd PWD             Password to be able to publish messages.
      --usock USOCK         UNIX Socket file for aiows server
      --host HOST           Server host
      --port PORT           Server port
      --reuse-addr REUSE_ADDR
                            Reuse host
      --reuse-port REUSE_PORT
                            Reuse port
      --url-prefix URL_PREFIX
                            API Endpoints prefix


HTTP API Endpoints
---------

**/channel/{channel_name}/**

This is WebSocket endpoint. Allows to subscribe to channel updates. 


**POST /channel/{channel_name}/**

Allows to share package to channel.

    Request Headers:
        - Package-Type(Text/bytes/json) - which type of package will be sent.
    
    Query Params:
        - pwd(str) - publishing password (by default: None)
    
    Request body:
        - any - publishing message
    
    Responses:
        - 403 - Wrong password
        - 400 - Failed to read request body
        - 201 - Published


Example

    import requests
    
    requests.post(
        url='http://127.0.0.1/channel/test-channel/?pwd=some-secure-pwd', 
        headers={'package-type': 'text'}, 
        data='Hello world'
    )
    
**POST /broadcast/**

Allows to bulk share packages between many channels.

    Query Params:
        - pwd(str) - publishing password (by default: None)
    
    Request body:
        - json(str) - publishing channels and messages as key=>value. Example:
    
        {
            "room:1": [{"text": "Hi all"}],
            "user:22": [{"json": {"notification": "You've got new friend"}}],
            "video:stream": [{"bytes": "\x031\x032\x033..."}, {"bytes": "\x031\x032\x033..."}]
        }
    
    Responses:
        - 403 - Wrong password
        - 400 - Failed to read request body
        - 201 - Published

Example

    import requests
    
    requests.post(
        url='http://127.0.0.1/broadcast/?pwd=some-secure-pwd', 
        json={
            "test-channel": [
                {"text": "Hello world"}
            ],
            "call:stream-channel": [
                {"bytes": "\x031\x032\x033..."}, 
                {"bytes": "\x031\x032\x033..."},
                {"bytes": "\x031\x032\x033..."},
                {"bytes": "\x031\x032\x033..."},
                {"bytes": "\x031\x032\x033..."},
                {"bytes": "\x031\x032\x033..."}
            ]
        }
    )