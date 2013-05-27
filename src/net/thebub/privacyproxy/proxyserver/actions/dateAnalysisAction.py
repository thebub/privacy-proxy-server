'''
Created on 23.05.2013

@author: dbub
'''
from net.thebub.privacyproxy.proxyserver.actions.analysisAction import AnalysisAction,analysisActions

import re
import PrivacyProxyAPI_pb2

class DateAnalysisAction(AnalysisAction):
    
    _type = PrivacyProxyAPI_pb2.date
    
    def match(self, data):
        matches = re.findall("(\\b(?:19|20)\d\d-(?:0?[1-9]|1[012])-(?:0?[1-9]|[12][0-9]|3[01])\\b)", data)
        
        wrongFormatMatches = re.findall("(?:\\b((?:19|20)\d\d)[/. ](0?[1-9]|1[012])[/. ](0?[1-9]|[12][0-9]|3[01])\\b)", data)
        
        for year,month,day in wrongFormatMatches:
            matches.append(year + "-" + month + "-" + day)
            
        wrongFormatMatches = re.findall("(?:\\b(0?[1-9]|[12][0-9]|3[01]).(0?[1-9]|1[012]).((?:19|20)\d\d)\\b)", data)
        
        for day,month,year in wrongFormatMatches:
            matches.append(year + "-" + month + "-" + day)
            
        wrongFormatMatches = re.findall("(?:\\b(0?[1-9]|1[012])[-/](0?[1-9]|[12][0-9]|3[01])[-/]((?:19|20)\d\d)\\b)", data)
        
        for month,day,year in wrongFormatMatches:
            matches.append(year + "-" + month + "-" + day)
        
        return matches
    
analysisActions.append(DateAnalysisAction)