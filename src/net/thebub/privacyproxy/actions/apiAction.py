'''
Created on 09.05.2013

@author: dbub
'''

from twisted.python import log

class APIAction(object):
    requiresAuthentication = False
    
    def __init__(self):
        log.msg("APIAction created")
        pass
    
    def process(self,data):
        log.msg("APIAction.process called")
        raise NotImplementedError(self.__class__, "This APIAction does not implement request processing")