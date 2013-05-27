'''
Created on 23.05.2013

@author: dbub
'''
from net.thebub.privacyproxy.proxyserver.actions.analysisAction import AnalysisAction,analysisActions

import re,string
import PrivacyProxyAPI_pb2

class CreditcardAnalysisAction(AnalysisAction):
    
    _type = PrivacyProxyAPI_pb2.creditcard

    def match(self,data):
        matches = []
        
        unformatedMatches = re.findall("(\\b(?:\\d[ -]*?){13,16}\\b)", data)
        
        for match in unformatedMatches:
            match = string.replace(match, "-", "")
            match = string.replace(match, " ", "")
            matches.append(match)
            
        return matches
    
analysisActions.append(CreditcardAnalysisAction)