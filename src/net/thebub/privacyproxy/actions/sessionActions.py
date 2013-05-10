'''
Created on 09.05.2013

@author: dbub
'''

from net.thebub.privacyproxy.actions.apiAction import APIAction

from twisted.python import log

class LoginAction(APIAction):
        
    def __init__(self):
        log.msg("LoginAction created")
        pass
    
class LogoutAction(APIAction):    
        
    def __init__(self):
        log.msg("LogoutAction created")
        self.requiresAuthentication = True
        pass