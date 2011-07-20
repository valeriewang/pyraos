#!/usr/bin/env python
#coding=utf-8
import ReadConfig
import web
import uuid
import urllib2
import sys
import time
import threading
import os

urls=("/GridSuccess","GridSuccess","/GridFail","GridFail")
app=web.application(urls,globals())

GridDic={}

class GridManager:
    def __init__(self,configpath):
        self.gridDic={}
        self.ParseConfig(configpath)
    def ParseConfig(self,path):
        cf=ReadConfig.CAppConfig(path)
        self.name=cf.get('gridmanager','name')
        self.grid_listener_port=cf.get('gridmanager','grid_listener_port')
        print '[GridManager {0} ParseConfig] listener_port={1}'.format(self.name,self.grid_listener_port)
    def Start(self):
        app.run()
    def CreateGrid(self,configpath):
        mygrid=GridInfo(configpath)
        result=mygrid.StartServer()
        if result==True:
            self.gridDic[mygrid.gridName]=mygrid
        else:
            print result
    def StartUpGrid(self,gridName):
        mygrid=GridDic[gridName]
    def AddServer(gridName,nodeName,serverConfigPath):
        mygrid=GridDic[gridName]
        mygrid.AddServer(nodeName,serverConfigPath)


class GridInfo:
    def __init__(self,path):
        self.gridConfigPath=path
        self.ParseConfig(path)
        self.state=False
    def ParseConfig(self,path):
        self.cf=ReadConfig.CAppConfig(path)
        #self.ID=uuid.uuid4()
        self.gridName=self.cf.get('grid','name')
        self.gridDataCenter=self.cf.get('grid','datacenterpath')
        self.girdVersion=self.cf.get('grid','version')
        self.gridType=self.cf.get('grid','type')
        self.NodeList=self.cf.get('grid','nodelist').split(',')
        print '[Grid {0}]DataCenter={1},Version={2},Type={3},NodeList={4}'.format(self.gridName,self.gridDataCenter,self.girdVersion,self.gridType,self.NodeList)
    def StartServer(self):
        file=self.gridDataCenter+'/gridconfig/'+os.path.basename(self.gridConfigPath)
        print 'file download path:',file
        #TODO upload config file
        print 'NodeList=',self.NodeList
        for name in self.NodeList:
            data="Method=StartServer,Name={0},file={1}".format(name,file)
            host=self.cf.get(name,'host')
            port=self.cf.get(name,'port')
            print '[Node {0} StartServer]host={1},port={2},file={3}'.format(name,host,port,file)
            url='http://'+host+':'+port+'/AddNode'
            print 'url=',url
            #req=urllib2.Request(url='http://'+host+':'+port+'/AddNode',data=data)
            response=urllib2.urlopen(url=url,data=data,timeout=200)
            result=response.read()
            print 'result:',result
            if not result=='True':
                return 'some problem in {0}'.format(name)
        return True
    def AddServer(self,nodeName,serverConfigPath):
        servercf=ReadConfig.CAppConfig(serverConfigPath)
#        file=self.gridDataCenter+'/gridconfig/'+os.path.basename(serverConfigPath)
#        url='http://'+self.cf.get(nodeName,'host')+':'+self.cf.get(nodeName)+'/AddServer'
#        data='Method=AddServer,Name={0},file={1}'.format(nodeName,file)
#        response=urllib2.urlopen(url=url,data=data,timeout=200)
#        result=response.read()
#        print 'result:',result

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
        


if __name__=='__main__':
    if len(sys.argv)==3:
        print '[GridManager]configpath=',sys.argv[2]
        configpath=sys.argv[2]
    else:
        configpath='./GridManager.ini'
    myGridManager=GridManager(configpath)
    t=threading.Thread(target=myGridManager.Start)
    t.start()
    time.sleep(1)
    print '[test]now create gridA'
#    myGridManager.CreateGrid('./gridconfig/gridA.ini')
    myGridManager.CreateGrid('./gridconfig/GridB.ini')
#    myGridManager.AddServer('GridB','Node2','../gridconfig/server1.ini')
    #myGridManager.AddUser('GridA','test','server','1234','myemail')
    #myGridManager.AddRegion('GridA','regiontest',1010,1010,9013)
#    myGridManager.AddUser('GridB','test','server','1234','myemail')
#    myGridManager.AddRegion('GridB','regiontest',1010,1010,9013)