
import subprocess
import MySQLdb
import uuid
import chilkat
import os
import xmlrpclib
import urllib, urllib2
import xml.dom.minidom
import time




class Grid:
    def __init__(self,configpath):
        self.configpath=configpath
        self.ParseConfig(configpath)
    def ParseConfig(self,path):
        cf=ConfigParser.ConfigParser()
        cf.read(path)
        self.name=cf.get('grid','name')
        self.type=cf.get('grid','type')
        self.version=cf.get('grid','version')
        print 'name='+self.name+' type='+self.type+' version='+self.version
        self.DataServerPath=cf.get('grid','DataServerPath')
        self.grid_port=cf.get('grid','DataServerConfigPath')
        self.node_port=cf.get('grid','RegionDataPath')
        self.GatherPath=cf.get('grid','GatherPath')
        self.serverlist=cf.get('grid','serverlist').split(',')
        
    def BuildServer(self):
        print self.serverlist
        mydb=DataBase(dblist=self.serverlist,host="localhost",username="opensim",password="1234")
        mydb.StartUp()
        mydb.PrepDatabase()
        if self.IsGrid():
            self.robust=RobustServer(self.serverlist[0],self.configpath,self.version)
            self.opensim=[]
            for osname in self.serverlist[1:len(self.serverlist)]:
                myopensim=GridOpenSimServer(osname,self.configpath,self.version)
    def IsGrid(self):
        return self.type=='grid'

class ServerInstant:
    ServerDataCenter="http://localhost/"
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
        url=self.ServerDataCenter+'server/'+self.Version+self.fileType
        print "[GetServer]url:"+url
        dst=self.loc+self.Version+self.fileType
        print "dst:"+dst
        
        if not os.path.exists(dst):
            print "begin get server from "+url
            response=urllib2.urlopen(url)
            output=open(dst,'wb')
            output.write(response.read())
            output.close()
            print "server download ok"
        else:
            print "server data exists"
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
        if os.path.exists(self.loc+self.name):
            for root, dirs, files in os.walk(self.loc+self.name, topdown=False):
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
        self.soProc=subprocess.Popen(["start {0} -console rest".format(self.loc+self.name+"/"+self.app)],cwd=self.loc+self.name+"/",shell=True)
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
    def __init__(self,name,path,version):
        self.app="Robust.exe"
        self.ParseConfig(name,path)
        ServerInstant.__init__(self,self.name,"Robust",self.loc,version)
        self.GetServer()
        #self.InstallServer()
        self.SetConfig()
        self.StartUp()
        time.sleep(10) #check if the server startup
        self.CreateUser()
    def ParseConfig(self,name,path):
        self.name=name
        cf=ConfigParser.ConfigParser()
        cf.read(path)
        print 'robust server name:'+name
        self.loc=cf.get(name,'Location')
        self.DBProvider=cf.get(name,'DBProvider')
        self.ConnString=cf.get(name,'ConnString')
        self.DBTable=self.ConnString.split(';')[1].split('=')[1]
        print 'robust database table is '+self.DBTable
        self.RemoteUser=cf.get(name,"RemoteUser")
        self.RemotePsw=cf.get(name,"RemotePsw")
        self.RemotePath=cf.get(name,"RemotePath")
        self.RemotePort=cf.get(name,'RemotePort')
        self.LoginPath=cf.get(name,'loginhost')
        self.AssetLoader=cf.get(name,'AssetLoader')
        print 'robust login path is '+self.LoginPath
        ulist=cf.get(name,"UserList").split(';')
        self.userlist=[]
        for userstring in ulist:
            print "user:"+userstring
            user=User(userstring)
            self.userlist.append(user)
    def SetConfig(self):
        configtype="Robust.ini"
        source=self.ServerDataCenter+"config/"+configtype
        dst=self.loc+self.name+"/"+configtype
        print 'get {0} from {1} to {2}'.format(configtype,source,dst)
        response=urllib2.urlopen(source)
        output=open(dst,'w')
        s=''
        for line in response.readlines():
            s=s+line.lstrip()
        output.write(s)
        output.close()
        cf=CAppConfig(dst)
        cf.set('DatabaseService','StorageProvider','\"'+self.DBProvider+'\"')
        cf.set('DatabaseService','ConnectionString','\"'+self.ConnString+'\"')
        #cf.set('AssetService','AssetLoaderEnabled',self.AssetLoader)
        cf.set('Network','ConsoleUser',self.RemoteUser)
        cf.set('Network','ConsolePass',self.RemotePsw)
        cf.set('Network','ConsolePort',self.RemotePort)
        fp=open(dst,'wb')
        cf.write(fp)
        fp.close()
    def CreateUser(self,startRegionX=128,startRegionY=128):
        print "remotepath="+self.RemotePath
        console=UserConsoleClient(self.RemotePath)
        for user in self.userlist:
            cmd="create user "+user.firstname+" "+user.lastname+" "+user.password+" "+user.email
            print "[create user]cmd="+cmd
            console.do_cmd(cmd)
        console.close()

class GridOpenSimServer(ServerInstant):
    def __init__(self,name,path,version):
        self.app="opensim.exe"
        self.ParseConfig(name,path)
        ServerInstant.__init__(self,self.name,"OpenSim",self.loc,version)
        self.GetServer()
        #self.InstallServer()
        self.SetConfig()
        self.SetRegions()
        self.StartUp()
        time.sleep(10) #check if the server startup
        #self.EditEstate()
    def ParseConfig(self,name,path):
        self.name=name
        cf=ConfigParser.ConfigParser()
        cf.read(path)
        print 'server name is '+name
        self.loc=cf.get(name,'Location')
        self.DBProvider=cf.get(name,'DBProvider')
        self.ConnString=cf.get(name,'ConnString')
        self.DBTable=self.ConnString.split(';')[1].split('=')[1]
        print 'database table is '+self.DBTable
        self.RemoteUser=cf.get(name,"RemoteUser")
        self.RemotePsw=cf.get(name,"RemotePsw")
        self.RemotePath=cf.get(name,"RemotePath")
        self.RemotePort=cf.get(name,'RemotePort')
        self.httplistenerport=cf.get(name,"httplistenerport")
        rlist=cf.get(name,"Regions").split(';')
        self.RegionsList=[]
        for regionstring in rlist:
            print "region:"+regionstring
            region=Region(regionstring)
            self.RegionsList.append(region)
    def SetConfig(self):
        configtype="OpenSim.ini"
        source=self.ServerDataCenter+"config/"+configtype
        dst=self.loc+self.name+"/"+configtype
        response=urllib2.urlopen(source)
        output=open(dst,'wb')
        s=''
        for line in response.readlines():
            s=s+line.lstrip()
        output.write(s)        
        output.close()
        cf=CAppConfig(dst)
        cf.set('Architecture','Include-Architecture',"config-include/Grid.ini")
        cf.set('Network','http_listener_port',self.httplistenerport)
        cf.set('Network','ConsoleUser',self.RemoteUser)
        cf.set('Network','ConsolePass',self.RemotePsw)
        cf.set('Network','ConsolePort',self.RemotePort)
        fp=open(dst,'wb')
        cf.write(fp)
        fp.close()
        

        configtype="GridCommon.ini"
        source=self.ServerDataCenter+"config/"+configtype
        dst=self.loc+self.name+"/config-include/"+configtype
        response=urllib2.urlopen(source)
        output=open(dst,'wb')
        s=''
        for line in response.readlines():
            s=s+line.lstrip()
        output.write(s)         
        output.close()
        cf=CAppConfig(dst)
        cf.set('DatabaseService','Storage',self.DBProvider)
        cf.set('DatabaseService','ConnectionString',self.ConnString)
        fp=open(dst,'wb')
        cf.write(fp)
        fp.close()
        
    def SetRegions(self):
        dst=self.loc+self.name+"/Regions/Regions.ini"
        fp=open(dst,'w')
        fp.close()
        cf=ConfigParser.ConfigParser()
        cf.read(dst)
        for region in self.RegionsList:
            cf.add_section(region.name)
            cf.set(region.name,'RegionUUID',region.uuid)
            cf.set(region.name,'Loction',region.locx+','+region.locy)
            cf.set(region.name,'InternalAddress','0.0.0.0')
            cf.set(region.name,'InternalPort',region.port)
            cf.set(region.name,'AllowAlternatePorts','False')
            cf.set(region.name,'ExternalHostName','SYSTEMIP')
        fp=open(dst,'wb')
        cf.write(fp)
        fp.close()
        
    def LoadRegions(self):
        console=UserConsoleClient(self.RemotePath)
        for region in self.RegionList:
            cmd="change region "+region.name
            console.do_cmd(cmd)
            cmd='load oar '+self.oar
            console.do_cmd(cmd)
        console.close()
#    def EditEstate(self):
#        print self.RemotePath
#        console=UserConsoleClient(self.RemotePath)
#        cmd="MyEatate"
#        console.do_cmd(cmd)
#        cmd="test"
#        console.do_cmd(cmd)
#        cmd="user"
#        console.do_cmd(cmd)
#        for Region in self.RegionList:
#            cmd="yes"
#            console.do_cmd(cmd)
#        console.close()
        
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
class User:
    def __init__(self,userstring):
        self.firstname,self.lastname,self.password,self.email=userstring.split(',')
class Region:
    def __init__(self,regionstring):
        self.uuid=uuid.uuid4()
        self.name,self.locx,self.locy,self.port,self.oar=regionstring.split(',')

class UserConsoleClient():

   def __init__(self, addr):
       self.addr = addr
       url = self.addr + 'StartSession/'

       params = urllib.urlencode({
           'USER': 'User',         # REST username
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
       url = self.addr + 'SessionCommand/'
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



       
if __name__=='__main__':
    myGridManager=GridManager('./MainConfig.ini')
    myGridManager.Start()
#    mygrid=Grid('./MainConfig.ini')
#    mygrid.BuildServer()
