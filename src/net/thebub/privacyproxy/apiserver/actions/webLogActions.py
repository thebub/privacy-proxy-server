'''
Created on 10.05.2013

@author: dbub
'''

from net.thebub.privacyproxy.apiserver.actions.apiAction import APIAction

import PrivacyProxyAPI_pb2

class GetWebLogWebsitesAction(APIAction):
    '''
    This action returns all websites the user has visited
    '''
    
    requiresAuthentication = True
    command = PrivacyProxyAPI_pb2.getWebpages
    
    def process(self, data):
        '''
        Get the websites the user has visisted from the databse and construct response objects
        '''
        self.dbConnection.query(("""SELECT website.id,website.url FROM website_log, website WHERE website_log.user_id = %s AND website_log.website_id = website.id;""",(self.userID,)))
        
        responseData = PrivacyProxyAPI_pb2.WebLogWebsitesResponse()
        
        # For each entry in the query result, create a website object
        for websiteID, url in self.dbConnection.fetchall():
            website = responseData.pages.add()
            website.id = websiteID
            website.website = url
        
        return self._returnSuccess(responseData)
    
class GetWebLogWebsiteDataAction(APIAction):
    '''
    Get the private data objects, which were disclosed to the specified webpage
    '''    
    
    requiresAuthentication = True
    command = PrivacyProxyAPI_pb2.getWebpageData
      
    def process(self, data):
        '''
        Get the data for the supplied website ID and construct response objects
        '''
        
        requestData = PrivacyProxyAPI_pb2.WebLogWebsiteDataRequest()
        requestData.ParseFromString(data)
        
        # Query all visit entries
        self.dbConnection.query(("""SELECT website_visit.id, website_visit.visitdate FROM website_visit WHERE website_visit.website_log_user_id = %s AND website_log_website_id = %s;""",(self.userID,requestData.id)))
                
        responseData = PrivacyProxyAPI_pb2.WebLogWebsiteDataResponse()
        responseData.id = requestData.id
        
        for visitID, visitdate in self.dbConnection.fetchall():
            websiteData = responseData.data.add()
            websiteData.date = visitdate.isoformat(' ')
            
            # For each visit, get all data entries
            self.dbConnection.query(("""SELECT user_data.id, user_data.type, user_data.description FROM user_data, visit_data WHERE visit_data.user_data_id = user_data.id AND user_data.user_id = %s AND visit_data.website_visit_id = %s;""",(self.userID,visitID)))
            
            for dataID, entryType, description in self.dbConnection.fetchall():
                personalDataEntry = websiteData.entry.add()
                personalDataEntry.id = dataID
                personalDataEntry.type = entryType
                personalDataEntry.description = description
        
        return self._returnSuccess(responseData)