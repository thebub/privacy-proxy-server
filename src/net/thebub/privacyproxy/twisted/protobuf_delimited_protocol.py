'''
Created on 14.05.2013

@author: dbub
'''
from twisted.internet.protocol import Protocol
from twisted.python import log

from google.protobuf.internal.decoder import _DecodeVarint
from google.protobuf.internal.encoder import _VarintEncoder

class ProtobufDelimitedProtocol(Protocol, object):
    '''
    This class provides a base protocol for twisted using VarINT encoded Protobuf messages. 
    '''
    
    _factory = None

    def __init__(self, factory):
        '''
        Init the protocol
        '''
        super(ProtobufDelimitedProtocol,self).__init__()
        
        self._factory = factory
        
        self.varint_encoder = _VarintEncoder()
        self.varint_decoder = _DecodeVarint
        
    def messageReceived(self, message):
        '''
        Method stub, which is called after a encoded message was received
        ''' 
        raise NotImplementedError
   
    def dataReceived(self, data):
        '''
        This method is called whenever data was received on the socket
        '''    
        data_length = len(data)
            
        # Decode the length of the expected message
        (size, pos) = self.varint_decoder(data, 0)
        
        if data_length - (size + pos) < 0:
            # TODO: Save buffer and wait for more data
            log.msg()
        
        # Use the specified class to decode the message
        message = self._message_class()
        message.ParseFromString(data[pos:size + pos])
        
        # Pass the decoded message to the message received function
        self.messageReceived(message)

    def sendMessage(self, message):
        '''
        Send a VarINT encoded message over the socket
        '''
        serialized = message.SerializeToString()
        serializedLen = len(serialized)
        
        self.varint_encoder(self.transport.write, serializedLen)
        self.transport.write(serialized)    