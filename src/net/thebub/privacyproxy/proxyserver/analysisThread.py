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

# Instantiate the analysis queue, hosting the AnalysisThreads
analysisQueue = Queue.Queue()

class AnalysisThread(threading.Thread):
    '''
    This class provides the implementation of the threads executing the analysis of the request data
    '''
    implements(interfaces.ILoggingContext)
    
    def __init__(self,dbHost,dbUser,dbPassword,dbDatabase):
        '''
        Init the thread and configure the database
        '''
        threading.Thread.__init__(self)
        self._dbConnection = DB(dbHost, dbUser, dbPassword, dbDatabase)
            
    def logPrefix(self):
        '''
        Configure the log prefix for twisted logging
        '''    
        return self.__class__.__name__ + "(" + self.getName() + ")"
    
    def _getUserDataSalt(self,userID):
        '''
        Return the data salt of the corresponding user
        '''
        self._dbConnection.query(("""SELECT data_salt FROM user WHERE id = %s;""",(userID,)))
        
        if self._dbConnection.rowcount() == 1:
            return self._dbConnection.fetchone()[0]
        
        return None
    
    def analyzeData(self,data,userID,dataSalt):
        '''
        Run the request parameters thru all the available analyisis engines
        '''
        analysisResults = []
        
        for analysisEngine in analysisActions:
            engine = analysisEngine(self,userID,dataSalt)
            analysisResults.extend(engine.analyze(data))
            
        return analysisResults
            
    def storeEntries(self,userID,url,date,entries):
        '''
        Store the found personal data entries into the database
        '''
        websiteID = None
        visitID = None
        
        # Check whether the url was visited anytime before
        self._dbConnection.query(("""SELECT id FROM website WHERE url = %s;""",(url,)))
        
        if self._dbConnection.rowcount() != 1:
            # If not create the website in the database
            self._dbConnection.query(("""INSERT INTO website(url) VALUES (%s);""",(url,)))
            
            if self._dbConnection.rowcount() == 1:
                # Get the ID of the newly inserted website
                websiteID = self._dbConnection.insertid()
            else:
                raise ValueError("Could not insert website")
        elif self._dbConnection.rowcount() == 1:
            # Get the ID of the visited url
            websiteID = self._dbConnection.fetchone()[0]
        
        # Check whether the user visited the website before
        self._dbConnection.query(("""SELECT 1 FROM website_log WHERE user_id = %s AND website_id = %s;""",(userID,websiteID)))
        
        if self._dbConnection.rowcount() != 1:
            # If the user has not visisted the website before create the user website link in the database
            self._dbConnection.query(("""INSERT INTO website_log(user_id,website_id) VALUES (%s,%s);""",(userID,websiteID)))
            
            if self._dbConnection.rowcount() != 1:
                raise ValueError("Could not create website_log entry")
        
        # Create the visit entry in the database
        self._dbConnection.query(("""INSERT INTO website_visit(website_log_user_id,website_log_website_id,visitdate) VALUES (%s,%s,%s);""",(userID,websiteID,date)))
        
        if self._dbConnection.rowcount() == 1:
            # Get the visit ID
            visitID = self._dbConnection.insertid()
        else:
            raise ValueError("Could not create visit entry")
        
        # For each found personal data disclosure, create a entry in the database
        for entry in entries:
            self._dbConnection.query(("""INSERT INTO visit_data(user_data_id,website_visit_id) VALUES (%s,%s);""",(entry,visitID)))
            
            if self._dbConnection.rowcount() != 1:
                raise ValueError("Could not insert data_visit entry")
        
        # Commit the transaction
        self._dbConnection.commit()
     
    def run(self):
        '''
        This method implements the main-loop of the thread
        '''
        log.msg("Thread starting",system=self.logPrefix())
        while True:
            # Wait for and get an analysis object from the queue
            analysisQueueEntry = analysisQueue.get()
            
            # Set the user ID
            userID = analysisQueueEntry['userID']
            
            # Get the data salt
            dataSalt = self._getUserDataSalt(userID)
        
            log.msg(analysisQueueEntry['url'],system=self.logPrefix())
                        
            analysisResults = []
            dataEntry = analysisQueueEntry['data']
            
            log.msg(dataEntry,system=self.logPrefix())
            
            # Analyze the provided data
            if type(dataEntry) == str:
                analysisResults.extend(self.analyzeData(dataEntry, userID, dataSalt))
            elif type(dataEntry) == list:
                for data in dataEntry:
                    analysisResults.extend(self.analyzeData(data, userID, dataSalt))
            elif type(dataEntry) == dict:
                for _,data in dataEntry.iteritems():
                    analysisResults.extend(self.analyzeData(data, userID, dataSalt))
            
            # If positive matches were found, insert them into the database
            if len(analysisResults) > 0:
                self.storeEntries(analysisQueueEntry['userID'],analysisQueueEntry['url'],analysisQueueEntry['date'],analysisResults)
            
            # Mark this queue entry finished
            analysisQueue.task_done()
    