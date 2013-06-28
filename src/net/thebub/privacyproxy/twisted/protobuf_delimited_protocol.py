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
    _unprocessed = b""

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
        allData = self._unprocessed + data
        offset = 0
          
        dataLength = len(allData)
                
        while (dataLength - offset) > 0:
                
            (size, pos) = self.varint_decoder(allData, offset)
            
            message_start = offset + pos
            message_end = message_start + size
            
            if dataLength < message_end:
                log.msg('Received data is too short. Waiting for next packet...')
                self._unprocessed = allData[offset:]
                return
            
            message = self._message_class()
            message.ParseFromString(allData[message_start:message_end])
            
            self.messageReceived(message)
            
            offset = message_end
        
        self._unprocessed = allData[offset:]        

    def sendMessage(self, message):
        '''
        Send a VarINT encoded message over the socket
        '''
        serialized = message.SerializeToString()
        serializedLen = len(serialized)
        
        self.varint_encoder(self.transport.write, serializedLen)
        self.transport.write(serialized)    