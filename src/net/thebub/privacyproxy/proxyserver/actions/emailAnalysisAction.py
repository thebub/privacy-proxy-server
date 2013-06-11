'''
Created on 23.05.2013

@author: dbub
'''

from net.thebub.privacyproxy.proxyserver.actions.analysisAction import AnalysisAction,analysisActions

import re
import PrivacyProxyAPI_pb2

class EmailAnalysisAction(AnalysisAction):
    '''
    This Analysis action searched for email addresses in any supplied data string
    '''
    
    _type = PrivacyProxyAPI_pb2.email

    def match(self,data):
        '''
        Search for email addresses in the supplied data
        '''
        return re.findall("(\\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,6}\\b)", data, flags=re.IGNORECASE)

# Add this action to the set of available actions
analysisActions.append(EmailAnalysisAction)