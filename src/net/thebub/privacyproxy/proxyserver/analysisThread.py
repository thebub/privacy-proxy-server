'''
Created on 20.05.2013

@author: dbub
'''
from zope.interface import implements

from twisted.internet import interfaces
from twisted.python import log

import Queue, threading

analysisQueue = Queue.Queue()

class AnalysisThread(threading.Thread):    
    implements(interfaces.ILoggingContext)
            
    def logPrefix(self):    
        return self.__class__.__name__ + "[" + self.getName() + "] - "
        
    def log(self,msg):
        log.msg(self.logPrefix() + msg)
 
    def run(self):
        self.log("Thread starting")
        while True:
            analysisData = analysisQueue.get()        
            self.log(str(analysisData))
    