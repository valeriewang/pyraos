#!/usr/bin/env python
#coding=utf-8
import web
import chilkat
import ReadConfig
import os
import MySQLdb
import grid
import urllib2

urls=("/AddNode","AddNode","/DeleteNode","DeleteNode")
app=web.application(urls,globals())

class NodeServer:
    def __init__(self):
        pass
    def StartServer(self):
        app.run()

class AddNode:
    def POST(self,path):
        datalist=web.data().split(',')
        print '[AddNode]datalist='+datalist
        for data in datalist:
            key,value=data.split('=')
            if key=='Method':
                self.method=value
            elif key=='Name':
                nodename=value
            elif key=='file':
                filepath=value
        #TODO get uploaded config file
        source=path+"/configfile/"+filepath
        response=urllib2.urlopen(source)
        
        temp=open('/',w)
        temp.write(response)
        temp.close()
        newNode=Node(name,'/')
    
class DeleteNode:
    def POST():
        pass

class Node:
    def __init__(self,name,configpath):
        self.name=name
        self.configpath=configpath
        self.ParseConfig(configpath)
    def ParseConfig(self,path):
        cf=ReadConfig.CAppConfig(path)
        self.DataCenter=cf.get('grid','datacenterpath')
        self.Version=cf.get('grid','version')
        self.type =cf.get('grid','type')
        self.loc=cf.get(self.name,'location')
        self.host=cf.get(self.name,'host')
        self.ServerList=cf.get(self.name,'serverlist').split(',')
        if cf.get(self.name,'dbprovider').lower()=='mysql':
            dbprovider="OpenSim.Data.MySQL.dll"
        #TODO add more database
        self.dbParams={'dbProvider':dbprovider,'dbHost':cf.get(self.name,'dbhost'),'dbUser':cf.get(self.name,'dbuser'),'dbPsw':cf.get(self.name,'dbpsw')}
        self.dbList=[]
        for name in self.ServerList:
            self.dbList.append(cf.get(name,'dbtable'))
    def BuildServers(self):
        print "[BuidlServers]download and uncompress server"
        self.GetServer()
        mydb=DataBase(dblist=self.dbList,host=self.dbParams['dbHost'],username=self.dbParams['dbUser'],password=self.dbParams['dbPsw'])
        mydb.PrepDatabase()
        print '[BuidlServers]mode is {0} ServerList is {1}'.format(self.type,self.ServerList)
        #TODO src should not be self.loc+'bin'
        if self.IsGrid():
            self.robust=grid.RobustServer(self.ServerList[0],self.configpath,self.host,self.loc,self.loc+'bin',self.dbParams)
            self.robust.StartUp()
            self.gridopensim=[]
            for osname in self.ServerList[1:len(self.ServerList)]:
                myopensim=grid.GridOpenSimServer(osname,self.configpath,self.host,self.loc,self.loc+'bin',self.dbParams)
                myopensim.StartUp()
                self.gridopensim.append(myopensim)
        else:
            pass
            #TODO 7/15/2010 startup a standalone mode server
    def ShutDownServer(self):
        pass
    def DeleteServer(self):
        pass
    def GetServer(self):
        #TODO more fileType
        self.fileType='.rar'
        source=self.DataCenter+'/server/'+self.Version+self.fileType
        dst=self.loc+self.Version+self.fileType
        if not os.path.exists(dst):
            try:
                print '[GetServer]begin get server from {0} to {1}'.format(source,dst)
                response=urllib2.urlopen(source)
                output=open(dst,'wb')
                output.write(response.read())
                output.close()
                print '[GetServer]server download ok'
            except:
                print '[GetServer]download fail'
        else:
            print "[GetServer]server data exists"
        print '[GetServer]uncompress server'
        if self.fileType==".rar":
            unCompress=chilkat.CkRar()
        elif self.fileType==".zip":
            unCompress=chilkat.CkZip()
        unCompress.Open(dst)
        unCompress.Unrar(self.loc)
        print '[GetServer]uncompress ok'
    def IsGrid(self):
        return self.type=='grid'

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
    server=NodeServer()
    server.StartServer()
    #mytestNode=Node('Node1','./MainConfig.ini')
    #mytestNode.BuildServers()