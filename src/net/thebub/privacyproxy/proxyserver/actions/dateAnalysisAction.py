'''
Created on 23.05.2013

@author: dbub
'''
from net.thebub.privacyproxy.proxyserver.actions.analysisAction import AnalysisAction,analysisActions

import re
import PrivacyProxyAPI_pb2

class DateAnalysisAction(AnalysisAction):
    '''
    This class implements an AnalysisAction, which searched for date sin the data
    '''
    
    _type = PrivacyProxyAPI_pb2.date
    
    def match(self, data):
        '''
        This method searches for dates in various representations in the user supplied data-
        '''
        # Find matches in the correct representation
        matches = re.findall("(\\b(?:19|20)\d\d-(?:0?[1-9]|1[012])-(?:0?[1-9]|[12][0-9]|3[01])\\b)", data)
        
        # Find matches in a non uniform representation
        wrongFormatMatches = re.findall("(?:\\b((?:19|20)\d\d)[/. ](0?[1-9]|1[012])[/. ](0?[1-9]|[12][0-9]|3[01])\\b)", data)
        
        # Transform the data into the uniform representation 
        for year,month,day in wrongFormatMatches:
            matches.append(year + "-" + month + "-" + day)
            
        # Find matches in a non uniform representation
        wrongFormatMatches = re.findall("(?:\\b(0?[1-9]|[12][0-9]|3[01]).(0?[1-9]|1[012]).((?:19|20)\d\d)\\b)", data)
        
        # Transform the data into the uniform representation
        for day,month,year in wrongFormatMatches:
            matches.append(year + "-" + month + "-" + day)
        
        # Find matches in a non uniform representation
        wrongFormatMatches = re.findall("(?:\\b(0?[1-9]|1[012])[-/](0?[1-9]|[12][0-9]|3[01])[-/]((?:19|20)\d\d)\\b)", data)
        
        # Transform the data into the uniform representation
        for month,day,year in wrongFormatMatches:
            matches.append(year + "-" + month + "-" + day)
        
        return matches

# Add this action to the set of available actions
analysisActions.append(DateAnalysisAction)