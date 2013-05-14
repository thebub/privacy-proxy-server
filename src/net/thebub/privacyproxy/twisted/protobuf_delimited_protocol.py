'''
Created on 14.05.2013

@author: dbub
'''
from twisted.internet.protocol import Protocol
from twisted.python import log

from google.protobuf.internal.decoder import _DecodeVarint
from google.protobuf.internal.encoder import _VarintEncoder

class ProtobufDelimitedProtocol(Protocol, object):
    
    _factory = None

    def __init__(self, factory):
        super(ProtobufDelimitedProtocol,self).__init__()
        
        self._factory = factory
        
        self.varint_encoder = _VarintEncoder()
        self.varint_decoder = _DecodeVarint
        
    def messageReceived(self, message):
        raise NotImplementedError
   
    def dataReceived(self, data):    
        data_length = len(data)
            
        (size, pos) = self.varint_decoder(data, 0)
        
        if data_length - (size + pos) < 0:
            # TODO: Save buffer and wait for more data
            log.msg()
        
        message = self._message_class()
        message.ParseFromString(data[pos:size + pos])
        
        self.messageReceived(message)

    def sendMessage(self, message):
        serialized = message.SerializeToString()
        serializedLen = len(serialized)
        
        self.varint_encoder(self.transport.write, serializedLen)
        self.transport.write(serialized)    