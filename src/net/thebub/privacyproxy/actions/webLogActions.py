'''
Created on 10.05.2013

@author: dbub
'''

from net.thebub.privacyproxy.actions.apiAction import APIAction
import APICall_pb2

class GetWebLogWebsitesAction(APIAction):
    
    requiresAuthentication = True
    command = APICall_pb2.getWebpages
    
    def process(self, data):
        self.protocol.dbConnection.query(("""SELECT website.id,website.url FROM website_log, website WHERE website_log.user_id = %s AND website_log.website_id = website.id;""",(self.protocol.userID,)))
        
        responseData = APICall_pb2.WebLogWebsitesResponse()
        
        for websiteID, url in self.protocol.dbConnection.fetchall():
            website = responseData.pages.add()
            website.id = websiteID
            website.website = url
        
        return self._returnSuccess(responseData)
    
class GetWebLogWebsiteDataAction(APIAction):    
    
    requiresAuthentication = True
    command = APICall_pb2.getWebpageData
      
    def process(self, data):        
        requestData = APICall_pb2.WebLogWebsiteDataRequest()
        requestData.ParseFromString(data)
        
        self.protocol.dbConnection.query(("""SELECT website_visit.id, website_visit.visitdate FROM website_visit WHERE website_visit.website_log_user_id = %s AND website_log_website_id = %s;""",(self.protocol.userID,requestData.id)))
                
        responseData = APICall_pb2.WebLogWebsiteDataResponse()
        responseData.id = requestData.id
        
        for visitID, visitdate in self.protocol.dbConnection.fetchall():
            websiteData = responseData.data.add()
            websiteData.date = visitdate.isoformat(' ')
            
            self.protocol.dbConnection.query(("""SELECT user_data.id, user_data.type, user_data.description FROM user_data, visit_data WHERE visit_data.user_data_id = user_data.id AND user_data.user_id = %s AND visit_data.website_visit_id = %s;""",(self.protocol.userID,visitID)))
            
            for dataID, entryType, description in self.protocol.dbConnection.fetchall():
                personalDataEntry = websiteData.entry.add()
                personalDataEntry.id = dataID
                personalDataEntry.type = entryType
                personalDataEntry.description = description
        
        return self._returnSuccess(responseData)