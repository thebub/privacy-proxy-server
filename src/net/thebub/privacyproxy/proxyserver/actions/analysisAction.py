'''
Created on 22.05.2013

@author: dbub
'''

import string, hashlib

analysisActions = []

class AnalysisAction(object):
    '''
    Abstract base class for analysis action the be executed on the request paramters.
    '''
    
    _type = None
    '''
    The PrivacyProxy data type analyzed by this action
    '''
    
    def __init__(self,analysisThread,userID,dataSalt):
        '''
        Initialize the analysis engine
        '''
        self._parentThread = analysisThread
        self._userID = userID
        self._dataSalt = dataSalt
        
    def match(self,data):
        '''
        Method stub for finding matches of the data type in the provided data 
        '''
        raise NotImplementedError()
    
    def _checkMatch(self,hashedMatch):
        '''
        Method checking the found matches against the database entries.
        If the hashes in the database and from the request data match, return the ID of the database entry.
        ''' 
        # Query the database for the combination of hash and user
        self._parentThread._dbConnection.query(("""SELECT id FROM user_data WHERE user_id = %s AND type = %s AND hash = %s;""",(self._userID,self._type,hashedMatch)))
        
        if self._parentThread._dbConnection.rowcount() == 1:
            # Return the ID of the match if one was found
            return self._parentThread._dbConnection.fetchone()[0]
        return False
    
    def analyze(self,data):
        '''
        This function takes the data and runs it thru the analysis process.
        It return the IDs of the found matches.
        '''
        matches = self.match(data)
        
        matchIDs = []
        
        # Iterate over the matches and check its correctness
        if len(matches) > 0:            
            for match in matches:            
                hashAlgorithm = hashlib.sha256()
                saltedMatch = string.join([match,self._dataSalt],"")
                hashAlgorithm.update(saltedMatch)
                hashedMatch = hashAlgorithm.hexdigest() 
                matchID = self._checkMatch(hashedMatch)
                
                if matchID:
                    matchIDs.append(matchID)
        
        # Return the found IDs         
        return matchIDs