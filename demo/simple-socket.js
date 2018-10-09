/**
 * Developed by Max
 * @constructor
 */
let SSocket = function (server) {
    this.ws = null;
    this.server = server;
    
    this.state = {
        connecting: false,
        connected: false
    };
};


/**
 * Connecting to socket server
 */
SSocket.prototype.connect = function (callback) {
    let self = this;

    // Check state to prevent double connection
    if ( self.state.connecting || self.state.connected ) {
        return;
    } else {
        self.state.connecting = true;
    }

    // Connecting to the server
    this.ws = new WebSocket(self.server);

    // Requesting new messages
    this.ws.onopen = function () {
        self.state.connected = true;
        self.state.connecting = false;
        console.log('[ws] Connected to server ' + self.server);
    };

    // Dispatch message
    this.ws.onmessage = function (msg) {
        callback(msg.data);
    };

    // Process error
    this.ws.onerror = function (e) {
        console.error('[ws]', e);
    };

    // Process close
    this.ws.onclose = function (e) {
        self.state.connected = self.connecting = false;
        console.error('[ws] Connecting lost. Sever: ' + self.server);
        console.error('[ws] Error: ', e);
        setTimeout(function () {
            self.connect();
        }, 1000);
    };
};
