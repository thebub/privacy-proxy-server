'''
Created on 13.05.2013

@author: dbub
'''

from twisted.web import proxy, http
from twisted.python import log
import hashlib, string, re, datetime

from net.thebub.privacyproxy.twisted.authProxyRequest import AuthProxyRequest
from net.thebub.privacyproxy.helpers.db import DB
from net.thebub.privacyproxy.proxyserver.analysisThread import analysisQueue,AnalysisThread

class PrivacyProxyRequest(AuthProxyRequest,object):
    '''
    The class ProvacyProxyRequest provides the implementation of the proxy request analysis and processing.
    It implements the AuthProxyInterface to support authentication checks. 
    '''
    
    _realmName = "PrivacyProxy"
    '''
    The name of the realm which is protected by AuthProxyRequest
    '''
    
    _userID = None
    '''
    The ID of the user which has successfully authenticated wioth the system
    '''
        
    def requiresUserAuth(self):
        '''
        This method indicated whether a authentication is required for this request
        '''
        return True
            
    def checkUserAuth(self, username, password):
        '''
        This method checks the authentication of the user using the provided username and password
        '''
        # Create the sha256 haslib object and the database connection
        hashAlgorithm = hashlib.sha256()
        self.dbConnection = DB(self.channel._dbHost, self.channel._dbUser, self.channel._dbPassword, self.channel._dbDatabase)
        
        # Query the database for the password salt of the specified user
        self.dbConnection.query(("""SELECT password_salt FROM user WHERE username = %s;""",(username,)))
        
        # If one row was returned the user exists and a password salt was found
        if self.dbConnection.rowcount() == 1:
            salt = self.dbConnection.fetchone()[0]
            saltedPassword = string.join([password,salt],"")
        
            # Reconstruct the hashed passowrd 
            hashAlgorithm.update(saltedPassword)
            passwordHash = hashAlgorithm.hexdigest()
            
            # Query the database for the combination of username and salted hash
            self.dbConnection.query(("""SELECT id FROM user WHERE username = %s AND password = %s;""",(username,passwordHash)))
            
            # If one row is returned the specified credentials are correct
            if self.dbConnection.rowcount() == 1:
                # Get the user id and store it within this object
                self._userID = self.dbConnection.fetchone()[0]
                
                # Indicate an successful authentication             
                return True
        
        # Indicate an authentication error 
        return False
    
    def analyzeURL(self):
        '''
        Analyze the URL for the domain basename and parameters
        '''
        url = self.path
        
        # Use the regex pattern to find the domain basename
        result = re.search('https?://(?:[a-zA-Z0-9\-]*\.)*(?:([a-zA-Z0-9\-]+\.[a-zA-Z0-9]{2,4})/?)(.*)',url)
        
        if result is None:
            return None
        
        # Return the found result
        return (result.group(1),result.group(2))
    
    def proxyRequestReceived(self):
        '''
        Process the request after a successful authentication
        '''
        
        # Process the request as a normal Proxy
        try:
            proxy.ProxyRequest.process(self)
        except KeyError:
            # A unsupported protocol was used. Return an error
            print "HTTPS is not supported at the moment!"
            self.finish()
            return
        
        # Analyze the URL for domain basename
        domain, _ = self.analyzeURL()
                
        analysisData = ""
        
        # If arguments were supplied during the request, queue them for analysis
        if len(self.args) > 0:
            # Construct a single string containing all parameters        
            for _, value in self.args.iteritems():
                for entry in value:
                    analysisData = analysisData + entry + ' '
            
            # Create the queue object for analysis
            analysisQueueEntry = {}
            analysisQueueEntry['userID'] = self._userID
            analysisQueueEntry['url'] = domain
            analysisQueueEntry['date'] = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            analysisQueueEntry['data'] = analysisData.strip()
            
            # Put the object in the queue
            analysisQueue.put(analysisQueueEntry)   
            
            self.dbConnection.diconnect()     

class PrivacyProxy(proxy.Proxy):
    '''
    This class implements the twisted HTTP proxy and is customized the use the PrivacyProxyRequest implementation and to configure the database
    '''
    requestFactory = PrivacyProxyRequest
    
    def __init__(self,dbHost,dbUser,dbPassword,dbDatabase):
        '''
        Configure the database and execute the super-constructor
        '''
        proxy.Proxy.__init__(self)
        
        self._dbHost = dbHost
        self._dbUser = dbUser
        self._dbPassword = dbPassword
        self._dbDatabase = dbDatabase

class PrivacyProxyFactory(http.HTTPFactory):
    '''
    This class implements the HTTP protocol factory.
    It initializes the analysis thread pool and manages the contained threads.
    '''
    
    _analysisThreadPool = []
    
    def __init__(self,dbHost,dbUser,dbPassword,dbDatabase,threadCount):
        '''
        Configure the database and create the desired amount of threads in the thread pool
        '''
        http.HTTPFactory.__init__(self)
        
        self._dbHost = dbHost
        self._dbUser = dbUser
        self._dbPassword = dbPassword
        self._dbDatabase = dbDatabase
        
        log.msg("Populating thread pool")
        
        # Create the thread instances
        for _ in range(threadCount):
            t = AnalysisThread(dbHost,dbUser,dbPassword,dbDatabase)
            t.daemon = True
            t.start()
            self._analysisThreadPool.append(t)
            
    def __del__(self):
        '''
        Deconstruct the protocol factory
        '''
        log.msg("Waiting for thread pool to finish work")
        #analysisQueue.join()
        log.msg("All threads finished")
    
    def buildProtocol(self, addr):
        '''
        Build the desired protocol
        '''
        return PrivacyProxy(self._dbHost,self._dbUser,self._dbPassword,self._dbDatabase)
    