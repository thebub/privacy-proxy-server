'''
Created on 22.05.2013

@author: dbub
'''

import string, hashlib

analysisActions = []

class AnalysisAction(object):
    
    _type = None
    
    def __init__(self,analysisThread,userID,dataSalt):
        self._parentThread = analysisThread
        self._userID = userID
        self._dataSalt = dataSalt
        
    def match(self,data):
        raise NotImplementedError()
    
    def _checkMatch(self,hashedMatch):
        self._parentThread.dbConnection.query(("""SELECT id FROM user_data WHERE user_id = %s AND type = %s AND hash = %s;""",(self._userID,self._type,hashedMatch)))
        
        if self._parentThread.dbConnection.rowcount() == 1:
            return self._parentThread.dbConnection.fetchone()[0]
        return False
    
    def analyze(self,data):
        matches = self.match(data)
        
        matchIDs = []
        
        if len(matches) > 0:            
            for match in matches:            
                hashAlgorithm = hashlib.sha256()
                saltedMatch = string.join([match,self._dataSalt],"")
                hashedMatch = hashAlgorithm.update(saltedMatch)
                matchID = self._checkMatch(hashedMatch)
                
                if matchID:
                    matchIDs.append(matchID)
                    
        return matchIDs
                
            
            
        