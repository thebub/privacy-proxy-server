'''
Created on 10.05.2013

@author: dbub
'''

from net.thebub.privacyproxy.actions.apiAction import APIAction
import APICall_pb2

class GetWebLogWebsitesAction(APIAction):    
        
    def __init__(self,protocol):
        super(GetWebLogWebsitesAction,self).__init__(protocol)
        self.requiresAuthentication = True
        pass
    
    def process(self, data):
        self.protocol.dbConnection.query(("""SELECT website.id,website.url FROM website_log, website WHERE website_log.user_id = %s AND website_log.website_id = website.id;""",(self.protocol.userID,)))
        
        response = APICall_pb2.APIResponse()
        response.command = APICall_pb2.getWebpages
        response.success = True
        response.errorCode = APICall_pb2.none
        
        responseData = APICall_pb2.WebLogWebsitesResponse()
        
        for websiteID, url in self.protocol.dbConnection.fetchall():
            website = responseData.pages.add()
            website.id = websiteID
            website.website = url
               
        response.data = responseData.SerializeToString()
        
        return response
    
class GetWebLogWebsiteDataAction(APIAction):    
        
    def __init__(self,protocol):
        super(GetWebLogWebsiteDataAction,self).__init__(protocol)
        self.requiresAuthentication = True
        pass
    
    def process(self, data):        
        requestData = APICall_pb2.WebLogWebsiteDataRequest()
        requestData.ParseFromString(data)
        
        self.protocol.dbConnection.query(("""SELECT website_visit.id, website_visit.visitdate FROM website_visit WHERE website_visit.website_log_user_id = %s AND website_log_website_id = %s;""",(self.protocol.userID,requestData.id)))
                
        response = APICall_pb2.APIResponse()
        response.command = APICall_pb2.getWebpageData
        response.success = True
        response.errorCode = APICall_pb2.none
        
        responseData = APICall_pb2.WebLogWebsiteDataResponse()
        responseData.id = requestData.id
        
        for visitID, visitdate in self.protocol.dbConnection.fetchall():
            websiteData = responseData.data.add()
            websiteData.date = visitdate.isoformat(' ')
            
            self.protocol.dbConnection.query(("""SELECT user_data.type, user_data.description FROM user_data, visit_data WHERE visit_data.user_data_id = user_data.id AND user_data.user_id = %s AND visit_data.website_visit_id = %s;""",(self.protocol.userID,visitID)))
            
            for entryType, description in self.protocol.dbConnection.fetchall():
                personalDataEntry = websiteData.entry.add()
                personalDataEntry.type = entryType
                personalDataEntry.description = description
        
        response.data = responseData.SerializeToString()
        
        return response