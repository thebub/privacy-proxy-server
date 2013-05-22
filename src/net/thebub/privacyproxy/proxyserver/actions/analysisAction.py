'''
Created on 22.05.2013

@author: dbub
'''

analysisActions = []

class AnalysisAction(object):
    
    def __init__(self,dataSalt):
        self._dataSalt = dataSalt
        
    def match(self,data):
        raise NotImplementedError()
    
    def analyze(self,data):
        raise NotImplementedError()
        