#!/usr/bin/env python
#coding=utf-8
import web
import chilkat
import ReadConfig
import os
import MySQLdb
import Server
import urllib2
import sys

DefaultServerPath='/server/'
DefaultConfigPath='/config/'
DefaultDataPath='/oar/'

urls=("/CreateNode","CreateNode",
      "/StartupNode","StartupNode",
      "/ShutDownNode","ShutDownNode",
      "/DeleteNode","DeleteNode",
      '/AddServer','AddServer',
      '/ShutDownServer','ShutDownServer',
      '/DeleteServer','DeleteServer',
      '/AddRegion','AddRegion',
      '/AddUser','AddUser')
app=web.application(urls,globals())
NodeDic={}
loc=''

class NodeServer:
    def __init__(self,configpath):
        self.ParseConfig(configpath)
        #register in GridManager
        self.Start()
    def ParseConfig(self,path):
        cf=ReadConfig.CAppConfig(path)
        self.name=cf.get('NodeServer','name')
        self.node_listener_port=cf.get('NodeServer','node_listener_port')
        loc=cf.get('NodeServer','loc')
        print '[NodeServer {0}]port={1}'.format(self.name,self.node_listener_port)
    def Start(self):
        app.run()

class CreateNode:
    def POST(self):
        datalist=web.data().split('&')
        print '[CreateNode]datalist=',datalist
        configdic=ParserData(datalist)
        if len(configdic)==0:
            return 'success=False&reason=config string is not right'
        newNode=Node(configdic)
        if newNode.BuildServers():
            return 'success=True'
        return 'success=False&reason=build server fail'
    def ParserData(datalist):
        configdic={}
        serverlist=[]
        serverdic={}
        for data in datalist:
            key,value=data.split('=')
            configdic[key]=value
        if configdic.has_key('serverList'):
            for strServer in dic['serverList']:
                serverParams=strServer.split(',')
                for param in serverParams:
                    key,value=param.split(':')
                    serverdic[key]=value
                serverlist.append(serverdic)
            configdic['serverList']=serverlist
        if self.HasPrimaryKey(configdic):
            return configdic
        else:
            return {}
    def HasPrimaryKey(dic):
        primaryKey=['NodeName','type','version','dbPrivider','dbHost','dbUser','dbPsw','serverList','resetDB','dataCenter']
        serverPrimaryKey=['ID','type','listener_port','dbTable']
        robustPrimaryKey=['login_port']
        gridopensimPrimaryKey=[]
        opensimPrimaryKey=[]
        for key in primaryKey:
            if not dic.has_key(key):
                print 'lost key {0}'.format(key)
                return False
        for server in dic['serverList']:
            for key in serverPrimaryKey:
                if not dic.has_key(key):
                    print 'lost key {0} in server'.format(key)
            if server['type']=='robust':
                for key in robustPrimaryKey:
                    if not dic.has_key(key):
                        print 'lost key {0} in server'.format(key)
            elif server['type']=='gridopensim':
                for key in gridopensimPrimaryKey:
                    if not dic.has_key(key):
                        print 'lost key {0} in server'.format(key)
            elif server['type']=='opensim':
                for key in opensimPrimaryKey:
                    if not dic.has_key(key):
                        print 'lost key {0} in server'.format(key)
            else:
                return False
        return True

class StartUpNode::
    def POST(self):
        
        
class AddServer:
    def POST(self):
        datalist=web.data().split(',')
#        print '[AddServer]datalist=',datalist
#        for data in datalist:
#            key,value=data.split('=')
#            print 'key={0},value={1}'.format(key,value)
#            if key=='Method':
#                self.method=value
#            elif key=='Name':
#                nodename=value
#            elif key=='file':
#                filepath=value
        
        
class DeleteNode:
    def POST():
        pass

class Node:
    def __init__(self,configDic):
        self.configDic=configDic
        self.dbDic={}
        for server in configDic['serverList']:
            self.dbDic[server['serverName']]=server['dbTable']
    def BuildServers(self):
        if not self.GetServer():
            return False
        try:
            mydb=DataBase(dblist=self.dbDic,host=self.configDic['dbHost'],username=self.configDic['dbUser'],password=self.configDic['dbPsw'])
            mydb.PrepDatabase()
        except:
            print 'db error'
            return False
        print '[BuidlServers]mode is {0} ServerList is {1}'.format(self.type,self.ServerList)
        try:
            if self.IsGrid():
                self.type='grid'
                self.gridopensim=[]
                for serverconfig in self.configDic['serverList']:
                    config={}
                    config['ID']=serverconfig['serverID']
                    config['loc']=loc+self.configDic['NodeName']+'/'+serverconfig['serverID']
                    config['src']=loc+self.configDic['NodeName']+'/'+self.configDic['version']
                    config['dbProvider']=self.configDic['dbProvider']
                    config['connString']="Data Source={0};Database={1};User ID={2};Password={3};Old Guids=true;".format(self.configDic['dbHost'],serverconfig['dbTable'],self.configDic['dbUser'],self.configDic['dbPsw'])
                    config['listener_port']=serverconfig['listener_port']
                    config['host']=self.configDic['host']
                    config['DataCenter']=self.configDic['dataCenter']
                    if serverconfig['type']=='robust':
                        config['login_port']=serverconfig['login_port']
                        self.robust=Server.RobustServer(config)
                    elif serverconfig['type']=='gridopensim':
                        myserver=Server.GridOpenSimServer(serverconfig)
                    self.gridopensim.append(myserver)
            else:
                self.type='standalone'
                config={}
                config['ID']=serverconfig['serverID']
                config['loc']=loc+self.configDic['NodeName']+'/'+serverconfig['serverID']
                config['src']=loc+self.configDic['NodeName']+'/'+self.configDic['version']
                config['dbProvider']=self.configDic['dbProvider']
                config['connString']="Data Source={0};Database={1};User ID={2};Password={3};Old Guids=true;".format(self.configDic['dbHost'],serverconfig['dbTable'],self.configDic['dbUser'],self.configDic['dbPsw'])
                config['listener_port']=serverconfig['listener_port']
                config['host']=self.configDic['host']
                config['DataCenter']=self.configDic['dataCenter']                
                self.opensim=Server.OpenSimServer(serverconfig)
        except:
            print 'server error'
            return False
    def StartupServers(self):
        if self.type =='grid':
            if not self.robust==null:
                if robust.state==False:
                    if not self.robust.StartUp():
                        return False
            for server in self.gridopensim:
                if server.state==False:
                    if not server.StartUp():
                        return False
            return True
        elif self.type='standalone':
            if opensim.state==False:
                return self.opensim.StartUp()
            return True
        else:
            return False
    def ShutDownServers(self):
        if self.type =='grid':
            for server in self.gridopensim:
                if server.state==True:
                    if not server.ShutDown():
                        return False
            if not self.robust==null:
                if robust.state==True:
                    if not self.robust.ShutDown():
                        return False
            return True
        elif self.type='standalone':
            if not opensim.state==True:
                return self.opensim.ShutDown()
            return True
        else:
            return False
    def DeleteServers(self):
        if self.type =='grid':
            for server in self.gridopensim:
                if not server.ShutDown():
                    return False
                if not server.Delete():
                    return False
                self.gridopensim.remove(server)
            if not self.robust==null:
                if not self.robust.ShutDown():
                    return False
                if not self.robust.Delete():
                    return False
                self.robust=null
            return True
        elif self.type='standalone':
            if not self.opensim.ShutDown():
                return False
            if not self.opensim.Delete():
                return False
            self.opensim=null
            return True
        else:
            return False
    def BuildServer(self,config):
        name=config['serverName']        
    def StartupServer(self):
        ${0}
    def ShutDownServer(self):
        ${0}
    def DeteteServer(self):
        ${0}
    def GetServer(self):
        print "[BuidlServers-GetServer]download server"
        #TODO how to get fileType
        self.fileType='.rar'
        source=self.DataCenter+DefaultServerPath+self.configDic['version']+self.fileType
        dst=self.loc+self.Version+self.fileType
        if not os.path.exists(dst):
            try:
                print '[GetServer]begin get server from {0} to {1}'.format(source,dst)
                response=urllib2.urlopen(source)
                output=open(dst,'wb')
                output.write(response.read())
                output.close()
                print '[GetServer]server download ok'
                return True
            except:
                print '[GetServer]download fail'
                return False
        else:
            print "[GetServer]server data exists"
            return True
    def IsGrid(self):
        print 'server type is {0}'.format(self.configDic['type'])
        return self.configDic['type']=='grid'

class DataBase:
    def __init__(self,username,password,dblist,host="localhost"):
        self.host=host
        self.user=username
        self.psw=password
        self.dbList=dblist
        self.state=True
    def PrepDatabase(self):
        if self.state==True:
            print "[PrepDataBase]begin prepare Database {0},{1},{2}".format(self.host,self.user,self.psw)
            self.conn=MySQLdb.connect(host=self.host,user=self.user,passwd=self.psw)
            cur=self.conn.cursor()
            for i in self.dbList:
                sql="CREATE DATABASE IF NOT EXISTS "+i
                print "[PrepDataBase]sql:"+sql
                cur.execute(sql)
            print "[PrepDataBase]Database is prepared"
    def ClearDatabase(self):
        if self.state==True:
            print "[ClearDatabase] begin clear database"
            self.conn=MySQLdb.connect(host=self.host,user=self.user,passwd=self.psw)
            cur=self.conn.cursor()
            for i in self.dbList:
                sql="DROP DATABASE IF EXISTS "+i
                print "[ClearDatabase] sql:"+sql
                cur.execute(sql)
            print "[ClearDatabase] database clear"
    def StartUp(self):
        pass
        #TODO start up database automatic
        #self.mysqlProc=subprocess.Popen([self.path+self.app],cwd=self.path)
        #print self.mysqlProc.returncode
        #print "DataBase have been run"
        #self.state=True
        #success=False
        #while not success:
        #    try:
        #        self.conn=MySQLdb.connect(host=self.host,user=self.user,passwd=self.psw)
        #        success=True
        #    except:
        #        success=False   




if __name__=='__main__':
    if len(sys.argv)==3:
        print '[NodeServer]configpath=',sys.argv[2]
        configpath=sys.argv[2]
    else:
        configpath='./NodeServer.ini'
    server=NodeServer(configpath)
    server.Start()
#    t=threading.Thread(target=server.Start)
#    t.start()
#    mytestNode=Node('Node1','./gridconfig/gridA.ini')
#    mytestNode.BuildServers()