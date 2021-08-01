import threading
from termcolor import colored
from lib.quirks.serverNetwork import serverNetwork


import re
import struct


chatMsgPatt = re.compile(r".*\\r\\x[0-9]{2}\\xfe")


class AutohostServer(threading.Thread):

    def __init__(self, host, port, hostedBy, bid, deliver, username):
        threading.Thread.__init__(self)
        self.serverNetwork = serverNetwork()
        self.serverNetwork.bind(host, port)
        self.username = username
        self.hostedby = hostedBy
        self.bid = bid
        self.deliver = deliver

    def autohostInterfaceSayChat(self, msg):
        self.serverNetwork.send(msg)

    def retrieveInfo(self, buf, prefix=b'\r\x00\xfe'):
        prefix_len = len(prefix)
        buf_len = len(buf)
        unpacked = struct.unpack(
            '{}s{}s'.format(
                prefix_len,
                buf_len -
                prefix_len),
            buf)

        res = None

        if prefix == b'\r\x00\xfe':
            res = unpacked[-1].decode('utf8')

        return res

    def run(self):
        while True:

            self.serverNetwork.receive()
            while self.serverNetwork.hasCmd():
                #print('autohost server interface triggered')

                receivedMsg = self.serverNetwork.nextCmd()
                #print('AUTOHOST SERVER!!!!!!!!!!!!!:'+str(self.serverNetwork.nextCmd()))
                if 'No clients connected, shutting down server' in receivedMsg:
                    ctl = {
                        "bid": self.bid,
                        "msg": 'exit',
                        "caller": self.hostedby,
                        "ttl": 0, "action": 'exit'}
                    self.deliver.put(ctl)

                if receivedMsg[0:3] == b'\r\x00\xfe':
                    msg2relay = self.retrieveInfo(receivedMsg)
                    print(
                        colored(
                            '[INFO]',
                            'green'),
                        colored(
                            self.username +
                            " forwarding to lobby: " +
                            receivedMsg,
                            'white'))
                    ctl = {
                        "bid": self.bid,
                        "msg": msg2relay,
                        "caller": self.hostedby,
                        "ttl": 0,
                        "action": 'sayBtlRoom'
                    }
                    self.deliver.put(ctl)
                else:
                    #print(colored('[INFO]', 'cyan'), "received: ", receivedMsg)
                    print(
                        colored(
                            '[INFO]',
                            'green'),
                        colored(
                            self.username +
                            " received: " +
                            receivedMsg,
                            'white'))
