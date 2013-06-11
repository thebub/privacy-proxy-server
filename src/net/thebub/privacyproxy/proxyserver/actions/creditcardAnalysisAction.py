'''
Created on 23.05.2013

@author: dbub
'''
from net.thebub.privacyproxy.proxyserver.actions.analysisAction import AnalysisAction,analysisActions

import re,string
import PrivacyProxyAPI_pb2

class CreditcardAnalysisAction(AnalysisAction):
    '''
    This class implements a AnalysisAction, which searches for credit card numbers and matches them against the database.
    '''
    
    _type = PrivacyProxyAPI_pb2.creditcard

    def match(self,data):
        '''
        Match for possible credit card numbers in the data
        '''
        matches = []
        
        # Use the regular expression to find possible credit card numbers
        unformatedMatches = re.findall("(\\b(?:\\d[ -]*?){13,16}\\b)", data)
        
        # Transform the credit card numbers in a unified representation
        for match in unformatedMatches:
            match = string.replace(match, "-", "")
            match = string.replace(match, " ", "")
            matches.append(match)
            
        return matches
    
# Add this action to the set of available actions
analysisActions.append(CreditcardAnalysisAction)