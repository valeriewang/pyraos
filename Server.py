import xmlrpclib
import subprocess
import MySQLdb
import uuid
import os
import xmlrpclib
import urllib, urllib2
import xml.dom.minidom
import time
import chilkat

import ReadConfig
import copytree

class ServerInstant:
    ConfigList={}
    state=False
    def __init__(self,configDic):
        self.State=False
        self.ID=configDic['ID']
        if configDic.has_key('app'):
            self.App=configDic['app']
        self.host=configDic['host']
        self.loc=configDic['loc']
        self.dbProvider=configDic['dbProvider']
        self.connString=configDic['connString']
        self.listener_port=configDic['listener_port']
        self.src=configDic['src']
        #something not good
        self.DataCenter=configDic['DataCenter']
    def InstallServer(self):
        try:
            print "[InstallServer]begin install server to {0}".format(self.loc)
            self.DeleteFolder(self.loc)
            os.mkdir(self.loc)
            print '[InstallServer]uncompress server'
            fileType=os.path.splitext(self.src)[1]
            print fileType,self.src,self.loc
            if fileType=='.rar':
                unCompress=chilkat.CkRar()
            unCompress.Open(self.src)
            unCompress.Unrar(self.loc)
            print "[InstallServer]install ok"
            return True
        except:
            return False
    def DeleteFolder(self,folder):
        if os.path.exists(folder):
            for root, dirs, files in os.walk(folder, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.removedirs(folder)
        
        
class RobustServer(ServerInstant):
    def __init__(self,configDic):
        ServerInstant.__init__(self,configDic)
        self.App="Robust.exe"
        self.login_port=configDic['login_port']
        self.RemoteUser='user'
        self.RemotePsw='1234'
        #TODO find a available port
        self.RemotePort='8070'
        self.RemotePath=self.host+':'+self.RemotePort
        self.userlist=[]
        if not self.InstallServer():
            return
        self.SetConfig()
    def SetConfig(self):
        #download basic config file
        configtype="Robust.ini"
        source=self.DataCenter+"/config/"+configtype
        dst=self.loc+"/"+configtype
        print '[RobustServer]download {0} from {1} to {2}'.format(configtype,source,dst)
        response=urllib2.urlopen(source)
        output=open(dst,'wb')
        s=''
        for line in response.readlines():
            s=s+line.lstrip()
        output.write(s)
        output.close()
        #modify config file
        cf=ReadConfig.CAppConfig(dst)
        cf.set('DatabaseService','StorageProvider','\"'+self.dbProvider+'\"')
        cf.set('DatabaseService','ConnectionString','\"'+self.connString+'\"')
        #cf.set('AssetService','AssetLoaderEnabled',self.AssetLoader)
        cf.set('Network','ConsoleUser',self.RemoteUser)
        cf.set('Network','ConsolePass',self.RemotePsw)
        cf.set('Network','ConsolePort',self.RemotePort)
        fp=open(dst,'wb')
        cf.write(fp)
        fp.close()
    def StartUp(self):
        if self.state==False:
            print "[Server {0}]startup server...".format(self.ID)
            workdir=self.loc+"/"
            app=self.loc+"/"+self.App
            print '[Server {0}]workdir is {1} and the app is {2}'.format(self.ID,workdir,app)
            self.soProc=subprocess.Popen(["start {0} -console rest".format(app)],cwd=workdir,shell=True)
            self.State=True
            #TODO check if the server startup
            time.sleep(10)
        else:
            print "[Server {0}]the server is already running".format(self.name)
        self.CreateDefaultUser()
    def ShutDown(self):
        if self.State==True:
            print "[ShutDown]begin..."
            console=UserConsoleClient(self.RemotePath)
            cmd='quit'
            console.do_cmd(cmd)
            console.close()
            print '[ShutDown]ok'
            self.State=False
    def Delete(self):
        print self.State
        if self.State==True:
            self.ShutDown()
            time.sleep(5)
        self.DeleteFolder(self.loc)
    def CreateDefaultUser(self):
        print "[CreateDefaultUser]begin..."
        console=UserConsoleClient(self.RemotePath)
        cmd='create user test user 1234 test.user@cysim.com'
        console.do_cmd(cmd)
        console.close()
        print '[CreateDefaultUser]ok'
        
    def CreateUser(self,userlist,startRegionX=128,startRegionY=128):
        print "remotepath="+self.RemotePath
        console=UserConsoleClient(self.RemotePath)
        for user in userlist:
            if user.firstname.lower()=='test' and user.lastname.lower()=='user':
                cmd='reset user password test user {0}'.format(user.password)
            else:
                cmd="create user "+user.firstname+" "+user.lastname+" "+user.password+" "+user.email
            print "[create user]cmd="+cmd
            console.do_cmd(cmd)
        console.close()

class GridOpenSimServer(ServerInstant):
    def __init__(self,configDic):
        ServerInstant.__init__(self,configDic)
        self.App="opensim.exe"
        self.robusturl=configDic['robusturl']
        self.remoteurl=self.host+':'+str(self.listener_port)
        self.InstallServer()
        self.SetConfig()
        #time.sleep(10) #TODO check if the server startup
    def StartUp(self):
        if self.State==False:
            print "[Server {0}]startup server...".format(self.ID)
            workdir=self.loc+"/"
            app=self.loc+"/"+self.App
            print '[Server {0}]workdir is {1} and the app is {2}'.format(self.ID,workdir,app)
            self.soProc=subprocess.Popen(["start {0}".format(app)],cwd=workdir,shell=True)
            self.State=True
            #TODO check if the server startup
#            time.sleep(20) 
#            self.LoadRegions(self.RegionsList)
        else:
            print "[Server {0}]the server is already running".format(self.name)
    def ShutDown(self):
        if self.State==True:
            self.server=xmlrpclib.Server(self.remoteurl)
            params = {}
            milliseconds=10
            if milliseconds is not 0:
                params['password']='1234'
                params['shutdown'] = 'delayed'
                params['milliseconds'] = milliseconds        
            self.server.admin_shutdown(params)
            self.State=False    
    def Delete(self):
            if self.State==True:
                self.ShutDown()
            self.DeleteFolder(self.loc)
    def SetConfig(self):
        configtype="OpenSim.ini"
        source=self.DataCenter+"/config/"+configtype
        dst=self.loc+"/"+configtype
        response=urllib2.urlopen(source)
        output=open(dst,'wb')
        s=''
        for line in response.readlines():
            s=s+line.lstrip()
        output.write(s)
        output.close()
        cf=ReadConfig.CAppConfig(dst)
        cf.set('Architecture','Include-Architecture',"config-include/Grid.ini")
        cf.set('Network','http_listener_port',self.listener_port)
        cf.set('RemoteAdmin','enabled','true')
        cf.set('RemoteAdmin','access_password','1234')
        fp=open(dst,'wb')
        cf.write(fp)
        fp.close()
        
        configtype="GridCommon.ini"
        source=self.DataCenter+"/config/"+configtype
        dst=self.loc+"/config-include/"+configtype
        response=urllib2.urlopen(source)
        output=open(dst,'wb')
        s=''
        for line in response.readlines():
            s=s+line.lstrip()
        output.write(s)
        output.close()
        cf=ReadConfig.CAppConfig(dst)
        cf.set('DatabaseService','StorageProvider','\"'+self.dbProvider+'\"')
        cf.set('DatabaseService','ConnectionString','\"'+self.connString+'\"')
        cf.set('AssetService','AssetServerURI',self.robusturl)
        cf.set('InventoryService','InventoryServerURI',self.robusturl)
        cf.set('GridService','GridServerURI',self.robusturl)
        cf.set('AvatarService','AvatarServerURI',self.robusturl)
        cf.set('PresenceService','PresenceServerURI',self.robusturl)
        cf.set('UserAccountService','UserAccountServerURI',self.robusturl)
        cf.set('GridUserService','GridUserServerURI',self.robusturl)
        cf.set('AuthenticationService','AuthenticationServerURI',self.robusturl)
        cf.set('FriendsService','FriendsServerURI',self.robusturl)
        cf.set('AssetService','AssetServerURI',self.robusturl)
        cf.set('AssetService','AssetServerURI',self.robusturl)
        fp=open(dst,'wb')
        cf.write(fp)
        fp.close()
        
    def AddRegion(self,regionList):
        print 'remoteurl:',self.remoteurl
        server=xmlrpclib.Server(self.remoteurl)
        for region in regionList:
            print region.name
            response=server.admin_create_region({'password':'1234','region_name':region.name,'listen_ip':'0.0.0.0','listen_port':region.port,'external_address':'SYSTEMIP','region_x':region.locx,'region_y':region.locy,'estate_name':'MyEstate'})
            print response
    def LoadRegions(self,regionList):
        server=xmlrpclib.Server(self.remoteurl)
        for region in regionList:
            source=self.DataCenter+'/oar/'+region.oar
            print source
            dst=self.loc+self.name+'/'+region.oar
            print 'load oar for'
            try:
                print '[GetOar]begin get data from '+source
                response=urllib2.urlopen(source)
                output=open(dst,'wb')
                output.write(response.read())
                output.close()
                print '[GetOar]region data download ok'
            except:
                print '[GetOar]download fail'
            response=server.admin_load_oar({'password':'1234','filename':region.oar,'region_name':region.name})
            print response
        
  
class OpenSimServer(ServerInstant):
    def __init__(self,configDic):
        ServerInstant.__init__(self,configDic)
        self.App='opensim.exe'
        self.remoteurl=self.host+':'+str(self.listener_port)
        self.InstallServer()
        self.SetConfig()
        self.SetDefaultRegion()
    def StartUp(self):
        if self.State==False:
            print "[Server {0}]startup server...".format(self.ID)
            workdir=self.loc+"/"
            app=self.loc+"/"+self.App
            print '[Server {0}]workdir is {1} and the app is {2}'.format(self.ID,workdir,app)
            self.soProc=subprocess.Popen(["start {0}".format(app)],cwd=workdir,shell=True)
            self.State=True
            #TODO check if the server startup
            #time.sleep(20) 
            #self.LoadRegions(self.RegionsList)
        else:
            print "[Server {0}]the server is already running".format(self.name)
    def ShutDown(self):
        if self.State==True:
            self.server=xmlrpclib.Server(self.remoteurl)
            params = {}
            milliseconds=10
            if milliseconds is not 0:
                params['password']='1234'
                params['shutdown'] = 'delayed'
                params['milliseconds'] = milliseconds        
            self.server.admin_shutdown(params)
            self.State=False    
    def Delete(self):
        if self.State==True:
            self.ShutDown()
        self.DeleteFolder(self.loc)
    
    def SetConfig(self):
        configtype="OpenSim.ini"
        source=self.DataCenter+"/config/"+configtype
        dst=self.loc+"/"+configtype
        response=urllib2.urlopen(source)
        output=open(dst,'wb')
        s=''
        for line in response.readlines():
            s=s+line.lstrip()
        output.write(s)        
        output.close()
        cf=ReadConfig.CAppConfig(dst)
        cf.set('Architecture','Include-Architecture',"\"config-include/Standalone.ini\"")
        cf.set('Network','http_listener_port',self.listener_port)
        cf.set('RemoteAdmin','enabled','true')
        cf.set('RemoteAdmin','access_password','1234')
        fp=open(dst,'wb')
        cf.write(fp)
        fp.close()
        
        configtype="StandaloneCommon.ini"
        source=self.DataCenter+"/config/"+configtype
        dst=self.loc+"/config-include/"+configtype
        print 'source={0},dst={1}'.format(source,dst)
        response=urllib2.urlopen(source)
        output=open(dst,'wb')
        output.write(response.read())         
        output.close()
    def SetDefaultRegion(self):
        dst=self.loc+"/Regions/Regions.ini"
        os.remove(dst)
        output=open(dst,'wb')
        cf=ReadConfig.CAppConfig(dst)
        cf.add_section('defaultRegion')
        cf.set('defaultRegion','RegionUUID',uuid.uuid4())
        cf.set('defaultRegion','Location','0,0')
        cf.set('defaultRegion','InternalAddress','0.0.0.0')
        cf.set('defaultRegion','InternalPort','9000')
        cf.set('defaultRegion','AllowAlternatePorts','False')
        cf.set('defaultRegion','ExternalHostName','SYSTEMIP')
        cf.write(output)
        output.close()
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
       url = self.addr + '/StartSession/'

       params = urllib.urlencode({
           'USER': 'user',         # REST username
           'PASS': '1234'        # REST password
       })
       print url
       data = urllib2.urlopen(url, params).read()
       print data
       dom = xml.dom.minidom.parseString(data)
       elem =  dom.getElementsByTagName('SessionID')
       self.sessionid = elem[0].childNodes[0].nodeValue

   def close(self):
       url = self.addr + '/CloseSession/'
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

       
if __name__=='__main__':
    print 'now no test run'
    #test robust mode  ok
#    robustConfigDic={'ID':'myrobust','loc':'E:/test/2/robust','src':'E:/test/2/0.3.rar','dbProvider':'OpenSim.Data.MySQL.dll','connString':'Data Source=127.0.0.1;Database=robust;User ID=opensim;Password=1234;Old Guids=true;','listener_port':8003,'login_port':8002,'host':'http://127.0.0.1','DataCenter':'http://localhost'}
#    robustServer=RobustServer(robustConfigDic)
#    robustServer.StartUp()
#    time.sleep(10)
#    robustServer.ShutDown()
#    time.sleep(10)
#    robustServer.Delete()
#    
#    gridopensimDic={'ID':'opensim0','loc':'E:/test/2/opensim0','src':'E:/test/2/0.3.rar','dbProvider':'OpenSim.Data.MySQL.dll','connString':'Data Source=127.0.0.1;Database=opensim0;User ID=opensim;Password=1234;Old Guids=true;','listener_port':9000,'robusturl':'http://127.0.0.1:8003','host':'http://127.0.0.1','DataCenter':'http://localhost'}
#    gridopensimServer=GridOpenSimServer(gridopensimDic)
#    gridopensimServer.StartUp()
#    time.sleep(10)
#    gridopensimServer.ShutDown()
#    time.sleep(10)
#    gridopensimServer.Delete()
    
    #test standalone mode  ok
#     opensimDic={'ID':'opensim','loc':'E:/test/2/opensim','src':'E:/test/2/0.3.rar','dbProvider':'OpenSim.Data.MySQL.dll','connString':'Data Source=127.0.0.1;Database=opensim;User ID=opensim;Password=1234;Old Guids=true;','listener_port':9000,'host':'http://127.0.0.1','DataCenter':'http://localhost'}
#     opensimServer=OpenSimServer(opensimDic)
#     opensimServer.StartUp()
#     time.sleep(10)
#     opensimServer.ShutDown()
#     time.sleep(10)
#     opensimServer.Delete()