#!/usr/bin/env python
#coding=utf-8

import subprocess
import MySQLdb
import uuid
import chilkat
import os
import xmlrpclib
import urllib, urllib2
import xml.dom.minidom
import time


class UserConsoleClient():

   def __init__(self, addr):
       self.addr = addr
       url = self.addr + 'StartSession/'

       params = urllib.urlencode({
           'USER': 'Test',         # REST username
           'PASS': '1234'        # REST password
       })
       print url
       data = urllib2.urlopen(url, params).read()
       print data
       dom = xml.dom.minidom.parseString(data)
       elem =  dom.getElementsByTagName('SessionID')
       self.sessionid = elem[0].childNodes[0].nodeValue

   def close(self):
       url = self.addr + 'CloseSession/'
       params = urllib.urlencode({
           'ID': self.sessionid
       })
       print urllib2.urlopen(url, params).read()

   def do_cmd(self, cmd):
       url = self.addr + '/SessionCommand/'
       params = urllib.urlencode({
           'ID': self.sessionid,
           'COMMAND': cmd
       })
       print urllib2.urlopen(url, params).read()

   def read_buffer(self):
       url = self.addr + 'ReadResponses/' + self.sessionid + '/'
       params = urllib.urlencode({
           'ID': self.sessionid
       })

       print urllib2.urlopen(url, params).read()

class ServerInstant:
    ServerDataCenter="http://localhost/server/"
    app=""
    loc=""
    ConfigList={}
    state=False
    Version="0.1"
    fileType=".rar"
    def __init__(self,name,type,location,version):
        self.id=uuid.uuid4()
        self.name=name
        self.type=type
        self.loc=location
        self.Version=version
    def GetServer(self):
        url=self.ServerDataCenter+self.Version+self.fileType
        print "[GetServer]url:"+url
        dst=self.loc+self.Version+self.fileType
        print "dst:"+dst
        
        if not os.path.exists(dst):
            print "begin get server"
            response=urllib2.urlopen(url)
            output=open(dst,'wb')
            output.write(response.read())
            output.close()
            print "server download ok"
        else:
            print "server data exists"
        self.InstallServer()
    def InstallServer(self):
        if self.fileType==".rar":
            unCompress=chilkat.CkRar()
        elif self.fileType==".zip":
            unCompress=chilkat.CkZip()
        print "begin installServer"
        dst=self.loc+self.Version+self.fileType
        unCompress.Open(dst)
        unCompress.Unrar(self.loc)
        print "install ok"
        if os.path.exists(self.loc+"robust"):
            for root, dirs, files in os.walk(self.loc+"robust", topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            #os.chdir(self.loc)
            os.removedirs(self.loc+self.name)
        os.rename(self.loc+"bin",self.loc+self.name)
    def StartUp(self):
        print "startup server..."
        print self.loc+self.name+"/"
        print self.loc+self.name+"/"+self.app
        self.soProc=subprocess.Popen(["start "+self.loc+self.name+"/"+self.app+" -console rest"],cwd=self.loc+self.name+"/",shell=True)
        state=True
        url="http://localhost:9070"
        self.server = xmlrpclib.Server(url)
        print self.server
    def ShutDown(self):
        params = {}
        if milliseconds is not 0:
            params['shutdown'] = 'delayed'
            params['milliseconds'] = milliseconds        
        self.server.admin_shutdown(params)
        state=False
        
class RobustServer(ServerInstant):
    def __init__(self,name,loc,version):
        ServerInstant.__init__(self,name,"Robust",loc,version)
    def SetConfig(self,Setting):
        configtype="Robust.ini"
        source=self.ServerDataCenter+"config/"+configtype
        dst=self.loc+self.name+"/"+configtype
        robustConfig=ConfigInstant(configtype,source,dst)
        self.ConfigList[configtype]=robustConfig
        if len(Setting)>0:
            robustConfig.Update(Setting)
            
    def CreateUser(self,firstName,lastName,password,email,startRegionX=128,startRegionY=128):
       # print "create user:"+firstName+" "+lastName+" "+password+" "+str(startRegionX)
       # self.server.admin_create_user({
#                    'password':'1234',
#                    'user_firstname' : firstName,
#                    'user_lastname' : lastName,
#                    'user_password' : password,
#                    'start_region_x' : str(startRegionX),
#                    'start_region_y' : str(startRegionY),
#                })
        remoteConsole="http://127.0.0.1:9070/"
        console=UserConsoleClient(remoteConsole)
        cmd="create user "+firstName+" "+lastName+" "+password
        console.do_cmd(cmd)
        console.close()

class OpensimServer(ServerInstant):
    RegionsConfigtype="Region.ini"
    def __init__(self,name,loc,version):
        ServerInstant.__init__(self,name,"Opensim",loc,version)
    def SetConfig(self,Setting):
        configtype="Opensim.ini"
        source=self.ServerDataCenter+"config/"+configtype
        dst=self.loc+self.name+"/"+configtype
        opensimConfig=ConfigInstant(configtype,source,dst)
        self.ConfigList[configtype]=opensimConfig
        if len(Setting)>0:
            opensimConfig.Update(Setting)
        configtype='GridCommon.ini'
        source=self.ServerDataCenter+"config/"+configtype
        dst=self.loc+self.name+"/config-include/"+configtype
        gridcommonConfig=ConfigInstant(configtype,source,dst)
        self.ConfigList[configtype]=gridcommonConfig
        if len(Setting)>0:
            gridcommonConfig.Update(Setting)
        
        
    def AddRegion(self,RegionName,port,Locx,locy):
        dst=self.loc+self.name+"/Regions/"+RegionsConfigtype
        output=open(dst,'wb')
        output.write(
        
    
    def CreateEstate(EstateName,FirstName,LastName):
        pass
    def SetEstate(RegionName,EstateName):
    def GetOar(self,RegionList):
        pass
        pass
        
        

class RegionInfo:
    RegionName=""
    port=""
    LocX=""
    LocY=""
    OarForRegion=""
    def __init__(self,RegionName,port,LocX,LocY,Oar=""):
        self.RegionName=RegionName
        self.port=port
        self.LocX=LocX
        self.LocY=LocY
        self.OarForRegion=Oar
    def SetOarForRegion(self,Oar):
        self.OarForRegion=Oar

class ConfigInstant:
    type=""
    config={}
    def __init__(self,type,source,dst):
        self.type =type
        self.dst=dst
        response=urllib2.urlopen(source)
        output=open(dst,'wb')
        output.write(response.read())
        output.close()
    def update(Setting):
        pass
                    
class DataBase:
    path="C:/wamp"
    app="/wampmanager.exe"
    host="localhost"
    user="opensim"
    psw="1234"
    dbList=[]
    conn=""
    state=False
    def __init__(self,host="localhost",username="opensim",password="1234",dblist=["robust","opensim0,opensim1,opensim2"],path="C:/wamp",app="/wampmanager.exe"):
        self.host=host
        self.app=app
        self.user=username
        self.psw=password
        self.path=path
        self.dbList=dblist
        
    def PrepDatabase(self):
        if self.state==True:
            print "[PrepDataBase]begin prepare Database"
            self.conn=MySQLdb.connect(host=self.host,user=self.user,passwd=self.psw)
            cur=self.conn.cursor()
            for i in self.dbList:
                sql="CREATE DATABASE IF NOT EXISTS "+i
                print "[PrepDataBase]sql:"+sql
                cur.execute(sql)
            print "Database is prepared"
    def ClearDatabase(self):
        if self.state==True:
            print "[ClearDatabase] begin clear database"
            self.conn=MySQLdb.connect(host=self.host,user=self.user,passwd=self.psw)
            cur=self.conn.cursor()
            for i in self.dbList:
                sql="DROP DATABASE IF EXISTS "+i
                print "[ClearDatabase] sql:"+sql
                cur.execute(sql)
    def StartUp(self):
        self.mysqlProc=subprocess.Popen([self.path+self.app],cwd=self.path)
        print self.mysqlProc.returncode
        print "DataBase have been run"
        self.state=True
        success=False
        while not success:
            try:
                self.conn=MySQLdb.connect(host=self.host,user=self.user,passwd=self.psw)
                success=True
            except:
                success=False
        



if __name__=="__main__":
    #startup a grid
    mydb=DataBase(dblist=["robust","opensim0"],host="localhost",username="opensim",password="1234")
    mydb.StartUp()
    mydb.PrepDatabase()
    
    myrobust=RobustServer("robust","E:/test/","0.1")
    #myrobust.GetServer()
    #myrobust.SetConfig({"ConnectionString":"Data Source=127.0.0.1;Database=vpkurobusttest;User ID=opensim;Password=1234;Old Guids=true;","AssetLoaderEnabled":"true"})
    myrobust.SetConfig([])
    myrobust.StartUp()
    time.sleep(10)
    myrobust.CreateUser("rui","wang","1234","")
    
    myopensim=OpensimServer("opensim","E/test/","0.1")
    myopensim.GetServer()
    myopensim.SetConfig([])
    myopensim.StartUp()
    EstateName=myopensim.CreateEstate("MyEstate","test","user")
    myopensim.SetEstate(RegionName,EstateName)
    