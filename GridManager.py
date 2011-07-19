#!/usr/bin/env python
#coding=utf-8
import ReadConfig
import web
import uuid
import urllib2

urls=("/GridSuccess","GridSuccess","/GridFail","GridFail","/AddGrid","AddGrid")
app=web.application(urls,globals())

GridDic={}

class GridManager:
    def __init__(self,configpath):
        self.ParseConfig(configpath)
    def ParseConfig(self,path):
        cf=ReadConfig.CAppConfig(path)
        self.name=cf.get('gridmanager','name')
        self.grid_listener_port=cf.get('gridmanager','grid_listener_port')
        self.node_listener_port=cf.get('gridmanager','node_listener_port')
    def Start(self):
        app.run()
    def CreateGrid(configpath):
        mygrid=GridInfo(configpath)
        mygrid.StartServer()
    
class GridSuccess:
    def Post(self,path):
        data=web.data()
        #TODO parse data
    def AddGrid(self,id):
        grid=GridDic[id]
        grid.state=True
    def DeleteGrid(self,id):
        grid=GridDic[id]
        grid.state=False    
        

class GridInfo:
    def __init__(self,path):
        self.path=path
        ParseConfig(paht)
        self.state=False
        StartServer()
    def ParseConfig(self,path):
        self.cf=ReadConfig.CAppConfig(path)
        self.ID=uuid.uuid4()
        self.Name=cf.get('grid','name')
        self.DataCenterPath=cf.get('grid','datacenterpath')
        self.Version=cf.get('grid','version')
        self.type=cf.get('grid','type')
        self.NodeList=cf.get('grid','nodelist').split(',')
    def StartServer(self):
        file="MainConfig.ini"
        #TODO upload config file
        for name in self.NodeList:
            data="Method=StartServer,Name={0},file={1}".format(name,file)
            host=cf.get(name,'host')
            req=urllib2.Request(url=host+':8070',data=data)
            response=urllib2.urlopen(req)
        
if __name__=='__main__':
    myGridManager=GridManager('./MainConfig.ini')
    myGridManager.Start()
    myGridManager.CreateGrid('../gridconfig/Grid.ini')
