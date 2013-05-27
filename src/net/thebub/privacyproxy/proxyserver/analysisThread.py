'''
Created on 20.05.2013

@author: dbub
'''
from zope.interface import implements

from twisted.internet import interfaces
from twisted.python import log

import Queue, threading

from net.thebub.privacyproxy.proxyserver.actions.analysisAction import analysisActions

from net.thebub.privacyproxy.helpers.db import DB

import net.thebub.privacyproxy.proxyserver.actions.creditcardAnalysisAction
import net.thebub.privacyproxy.proxyserver.actions.emailAnalysisAction
import net.thebub.privacyproxy.proxyserver.actions.dateAnalysisAction

analysisQueue = Queue.Queue()

class AnalysisThread(threading.Thread):    
    implements(interfaces.ILoggingContext)
    
    def __init__(self,dbHost,dbUser,dbPassword,dbDatabase):
        threading.Thread.__init__(self)
        self._dbConnection = DB(dbHost, dbUser, dbPassword, dbDatabase)
            
    def logPrefix(self):    
        return self.__class__.__name__ + "(" + self.getName() + ")"
    
    def _getUserDataSalt(self,userID):
        self._dbConnection.query(("""SELECT data_salt FROM user WHERE id = %s;""",(userID,)))
        
        if self._dbConnection.rowcount() == 1:
            return self._dbConnection.fetchone()[0]
        
        return None
    
    def analyzeData(self,data,userID,dataSalt):
        analysisResults = []
        
        for analysisEngine in analysisActions:
            engine = analysisEngine(self,userID,dataSalt)
            analysisResults.extend(engine.analyze(data))
            
        return analysisResults
            
    def storeEntries(self,userID,url,date,entries):
        websiteID = None
        visitID = None
        self._dbConnection.query(("""SELECT id FROM website WHERE url = %s;""",(url,)))
        
        if self._dbConnection.rowcount() != 1:
            self._dbConnection.query(("""INSERT INTO website(url) VALUES (%s);""",(url,)))
            
            if self._dbConnection.rowcount() == 1:
                websiteID = self._dbConnection.insertid()
            else:
                raise ValueError("Could not insert website")
        elif self._dbConnection.rowcount() == 1:
            websiteID = self._dbConnection.fetchone()[0]
        
        self._dbConnection.query(("""SELECT 1 FROM website_log WHERE user_id = %s AND website_id = %s;""",(userID,url)))
        
        if self._dbConnection.rowcount() != 1:
            self._dbConnection.query(("""INSERT INTO website_log(user_id,website_id) VALUES (%s,%s);""",(userID,websiteID)))
            
            if self._dbConnection.rowcount() != 1:
                raise ValueError("Could not create website_log entry")
            
        self._dbConnection.query(("""INSERT INTO website_visit(website_log_user_id,website_log_website_id,visitdate) VALUES (%s,%s,%s);""",(userID,websiteID,date)))
        
        if self._dbConnection.rowcount() == 1:
            visitID = self._dbConnection.insertid()
        else:
            raise ValueError("Could not create visit entry")
        
        for entry in entries:
            self._dbConnection.query(("""INSERT INTO visit_data(user_data_id,website_visit_id) VALUES (%s,%s);""",(entry,visitID)))
            
            if self._dbConnection.rowcount() != 1:
                raise ValueError("Could not insert data_visit entry")
        
        self._dbConnection.commit()
     
    def run(self):
        log.msg("Thread starting",system=self.logPrefix())
        while True:
            analysisQueueEntry = analysisQueue.get()
            
            userID = analysisQueueEntry['userID']
                                    
            dataSalt = self._getUserDataSalt(userID)
        
            log.msg(analysisQueueEntry['url'],system=self.logPrefix())
                        
            analysisResults = []
            dataEntry = analysisQueueEntry['data']
            
            log.msg(dataEntry,system=self.logPrefix())
                
            if type(dataEntry) == str:
                analysisResults.extend(self.analyzeData(dataEntry, userID, dataSalt))
            elif type(dataEntry) == list:
                for data in dataEntry:
                    analysisResults.extend(self.analyzeData(data, userID, dataSalt))
            elif type(dataEntry) == dict:
                for _,data in dataEntry.iteritems():
                    analysisResults.extend(self.analyzeData(data, userID, dataSalt))
            
            if len(analysisResults) > 0:
                self.storeEntries(analysisQueueEntry['userID'],analysisQueueEntry['url'],analysisQueueEntry['date'],analysisResults)
                
            analysisQueue.task_done()
    