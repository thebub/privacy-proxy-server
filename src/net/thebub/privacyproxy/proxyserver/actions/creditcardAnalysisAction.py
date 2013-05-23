'''
Created on 23.05.2013

@author: dbub
'''
from net.thebub.privacyproxy.proxyserver.actions.analysisAction import AnalysisAction,analysisActions

import re,string

class CreditcardAnalysisAction(AnalysisAction):

    def match(self,data):
        matches = []
        
        unformatedMatches = re.findall("(\\b(?:\\d[ -]*?){13,16}\\b)", data)
        
        for match in unformatedMatches:
            match = string.replace(match, "-", "")
            match = string.replace(match, " ", "")
            matches.append(match)
            
        return matches
    
analysisActions.append(CreditcardAnalysisAction)