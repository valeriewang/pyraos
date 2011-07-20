import xmlrpclib
import subprocess
import MySQLdb
import uuid
import os
import xmlrpclib
import urllib, urllib2
import xml.dom.minidom
import time
import ReadConfig
import copytree

class ServerInstant:
    ConfigList={}
    state=False
    def __init__(self,name,type,location,src):
        self.name=name
        self.type=type
        self.loc=location
        self.src=src
    def InstallServer(self):
        print "[InstallServer]begin install server to {0}".format(self.loc+self.name)
        if os.path.exists(self.loc+self.name):
            for root, dirs, files in os.walk(self.loc+self.name, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            #os.chdir(self.loc)
            os.removedirs(self.loc+self.name)
        copytree.copytree(self.src,self.loc+self.name)
        print "[InstallServer]install ok"
    def ShutDown(self):
        params = {}
        if milliseconds is not 0:
            params['shutdown'] = 'delayed'
            params['milliseconds'] = milliseconds        
        self.server.admin_shutdown(params)
        state=False
        
class RobustServer(ServerInstant):
    def __init__(self,name,path,host,loc,src,dbParams):
        self.app="Robust.exe"
        self.state=False
        self.host=host
        self.loc=loc
        self.dbParams=dbParams
        self.ParseConfig(name,path)
        ServerInstant.__init__(self,self.name,"Robust",loc,src)
        self.InstallServer()
        self.SetConfig()
    def ParseConfig(self,name,path):
        self.name=name
        cf=ReadConfig.CAppConfig(path)
        self.DataCenter=cf.get('grid','datacenterpath')
        self.dbTable=cf.get(name,'dbtable')
        self.RemoteUser=cf.get(name,"remoteuser")
        self.RemotePsw=cf.get(name,"remotepsw")
        self.RemotePort=cf.get(name,'remoteport')
        self.RemotePath="http://"+self.host+":"+self.RemotePort
        self.LoginPath=self.host+':'+cf.get(name,'loginport')
        self.AssetLoader=cf.get(name,'assetloader')
        print 'robust login path is '+self.LoginPath
        ulist=cf.get(name,"userlist").split(';')
        self.userlist=[]
        for userstring in ulist:
            print '[RobustServer]user:'+userstring
            user=User(userstring)
            self.userlist.append(user)
    def SetConfig(self):
        configtype="Robust.ini"
        source=self.DataCenter+"/config/"+configtype
        dst=self.loc+self.name+"/"+configtype
        print '[RobustServer]download {0} from {1} to {2}'.format(configtype,source,dst)
        response=urllib2.urlopen(source)
        output=open(dst,'w')
        s=''
        for line in response.readlines():
            s=s+line.lstrip()
        output.write(s)
        output.close()
        cf=ReadConfig.CAppConfig(dst)
        cf.set('DatabaseService','StorageProvider','\"'+self.dbParams['dbProvider']+'\"')
        connString="Data Source={0};Database={1};User ID={2};Password={3};Old Guids=true;".format(self.dbParams['dbHost'],self.dbTable,self.dbParams['dbUser'],self.dbParams['dbPsw'])
        cf.set('DatabaseService','ConnectionString','\"'+connString+'\"')
        #cf.set('AssetService','AssetLoaderEnabled',self.AssetLoader)
        cf.set('Network','ConsoleUser',self.RemoteUser)
        cf.set('Network','ConsolePass',self.RemotePsw)
        cf.set('Network','ConsolePort',self.RemotePort)
        fp=open(dst,'wb')
        cf.write(fp)
        fp.close()
    def StartUp(self):
        if self.state==False:
            print "[Server {0}]startup server...".format(self.name)
            workdir=self.loc+self.name+"/"
            app=self.loc+self.name+"/"+self.app
            print '[Server {0}]workdir is {1} and the app is {2}'.format(self.name,workdir,app)
            self.soProc=subprocess.Popen(["start {0} -console rest".format(app)],cwd=workdir,shell=True)
            state=True
            #TODO check if the server startup
            time.sleep(10) 
            
        else:
            print "[Server {0}]the server is already running".format(self.name)
        self.CreateDefaultUser()
        self.CreateUser(self.userlist)
                
    def CreateDefaultUser(self):
        print "[CreateDefaultUser]begin..."
        console=UserConsoleClient(self.RemotePath)
        for user in self.userlist:
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
    def __init__(self,name,path,host,loc,src,dbParams):
        self.app="opensim.exe"
        self.state=False
        self.host=host
        self.loc=loc
        self.dbParams=dbParams
        self.ParseConfig(name,path)
        ServerInstant.__init__(self,self.name,"GridOpenSim",self.loc,src)
        self.InstallServer()
        self.SetConfig()
        self.SetRegions()
        #time.sleep(10) #TODO check if the server startup
        #self.EditEstate()
    def StartUp(self):
        if self.state==False:
            print "[Server {0}]startup server...".format(self.name)
            workdir=self.loc+self.name+"/"
            app=self.loc+self.name+"/"+self.app
            print '[Server {0}]workdir is {1} and the app is {2}'.format(self.name,workdir,app)
            self.soProc=subprocess.Popen(["start {0}".format(app)],cwd=workdir,shell=True)
            state=True
            #TODO check if the server startup
            time.sleep(20) 
            self.LoadRegions(self.RegionsList)
        else:
            print "[Server {0}]the server is already running".format(self.name)
    
    def ParseConfig(self,name,path):
        self.name=name
        cf=ReadConfig.CAppConfig(path)
        self.DataCenter=cf.get('grid','datacenterpath')
        if cf.get(name,'computer')=='32':
            self.app='opensim.exe'
        else:
            self.app='OpenSim.32BitLaunch.exe'
        self.dbTable=cf.get(name,'dbtable')      
        self.httplistenerport=cf.get(name,"httplistenerport")
        self.remoteurl='http://'+self.host+':'+self.httplistenerport
        rlist=cf.get(name,"regions").split(';')
        self.RegionsList=[]
        for regionstring in rlist:
            print '[GridOpenSimServer {0}]region:{1}'.format(self.name,regionstring)
            region=Region(regionstring)
            self.RegionsList.append(region)
    def SetConfig(self):
        configtype="OpenSim.ini"
        source=self.DataCenter+"/config/"+configtype
        dst=self.loc+self.name+"/"+configtype
        print '[error]'+source
        response=urllib2.urlopen(source)
        output=open(dst,'wb')
        s=''
        for line in response.readlines():
            s=s+line.lstrip()
        output.write(s)        
        output.close()
        cf=ReadConfig.CAppConfig(dst)
        cf.set('Architecture','Include-Architecture',"config-include/Grid.ini")
        cf.set('Network','http_listener_port',self.httplistenerport)
        cf.set('RemoteAdmin','enabled','true')
        cf.set('RemoteAdmin','access_password','1234')
        fp=open(dst,'wb')
        cf.write(fp)
        fp.close()
        
        configtype="GridCommon.ini"
        source=self.DataCenter+"/config/"+configtype
        dst=self.loc+self.name+"/config-include/"+configtype
        response=urllib2.urlopen(source)
        output=open(dst,'wb')
        s=''
        for line in response.readlines():
            s=s+line.lstrip()
        output.write(s)         
        output.close()
        cf=ReadConfig.CAppConfig(dst)
        cf.set('DatabaseService','StorageProvider','\"'+self.dbParams['dbProvider']+'\"')
        connString="Data Source={0};Database={1};User ID={2};Password={3};Old Guids=true;".format(self.dbParams['dbHost'],self.dbTable,self.dbParams['dbUser'],self.dbParams['dbPsw'])
        cf.set('DatabaseService','ConnectionString','\"'+connString+'\"')
        fp=open(dst,'wb')
        cf.write(fp)
        fp.close()
        
    def SetRegions(self):
        dst=self.loc+self.name+"/Regions/Regions.ini"
        fp=open(dst,'w')
        fp.close()
        cf=ReadConfig.CAppConfig(dst)
        for region in self.RegionsList:
            print 'Region {0}:uuid={1},locx={2},locy={3},port={4}'.format(region.name,str(region.uuid),region.locx,region.locy,region.port)
            cf.add_section(region.name)
            cf.set(region.name,'RegionUUID',str(region.uuid))
            cf.set(region.name,'Location',region.locx+','+region.locy)
            cf.set(region.name,'InternalAddress','0.0.0.0')
            cf.set(region.name,'InternalPort',region.port)
            cf.set(region.name,'AllowAlternatePorts','False')
            cf.set(region.name,'ExternalHostName','SYSTEMIP')
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
    def __init__(self,name,path,host,loc,src,dbParams):
        self.app='opensim.exe'
        self.state=False
        self.host=host
        self.loc=loc
        self.dbParams=dbParams
        self.ParseConfig(name,path)
        ServerInstant.__init__(self,self.name,"OpenSim",self.loc,src)
        self.InstallServer()
        self.SetConfig()
        self.SetRegions()
    def StartUp(self):
        if self.state==False:
            print "[Server {0}]startup server...".format(self.name)
            workdir=self.loc+self.name+"/"
            app=self.loc+self.name+"/"+self.app
            print '[Server {0}]workdir is {1} and the app is {2}'.format(self.name,workdir,app)
            self.soProc=subprocess.Popen(["start {0}".format(app)],cwd=workdir,shell=True)
            state=True
            #TODO check if the server startup
            #time.sleep(20) 
            #self.LoadRegions(self.RegionsList)
        else:
            print "[Server {0}]the server is already running".format(self.name)
    def ParseConfig(self,name,path):
        self.name=name
        cf=ReadConfig.CAppConfig(path)
        self.DataCenter=cf.get('grid','datacenterpath')
        if cf.get(name,'computer')=='32':
            self.app='opensim.exe'
        else:
            self.app='OpenSim.32BitLaunch.exe'
        self.dbTable=cf.get(name,'dbtable')       
        self.httplistenerport=cf.get(name,"httplistenerport")
        r=cf.get(name,"regions")
        self.RegionsList=[]
        if not r=='null':
            rlist=r.split(';')
            for regionstring in rlist:
                print '[GridOpenSimServer {0}]region:{1}'.format(self.name,regionstring)
                region=Region(regionstring)
                self.RegionsList.append(region)
    def SetConfig(self):
        print 'aaaaaaaa'
        configtype="OpenSim.ini"
        source=self.DataCenter+"/config/"+configtype
        dst=self.loc+self.name+"/"+configtype
        print configtype,source,dst
        response=urllib2.urlopen(source)
        output=open(dst,'wb')
        s=''
        for line in response.readlines():
            s=s+line.lstrip()
        output.write(s)        
        output.close()
        cf=ReadConfig.CAppConfig(dst)
        cf.set('Architecture','Include-Architecture',"\"config-include/Standalone.ini\"")
        cf.set('Network','http_listener_port',self.httplistenerport)
        cf.set('RemoteAdmin','enabled','true')
        cf.set('RemoteAdmin','access_password','1234')
        fp=open(dst,'wb')
        cf.write(fp)
        fp.close()
        
        configtype="StandaloneCommon.ini"
        source=self.DataCenter+"/config/"+configtype
        dst=self.loc+self.name+"/config-include/"+configtype
        print 'source={0},dst={1}'.format(source,dst)
        response=urllib2.urlopen(source)
        output=open(dst,'wb')
        output.write(response.read())         
        output.close()
    def SetRegions(self):
        dst=self.loc+self.name+"/Regions/Regions.ini"
        cf=ReadConfig.CAppConfig(dst)
        if len(self.RegionsList)==0:
            cf.add_section('defaultRegion')
            cf.set('defaultRegion','RegionUUID',uuid.uuid4())
            cf.set('defaultRegion','Location','1000,1000')
            cf.set('defaultRegion','InternalAddress','0.0.0.0')
            cf.set('defaultRegion','InternalPort','9000')
            cf.set('defaultRegion','AllowAlternatePorts','False')
            cf.set('defaultRegion','ExternalHostName','SYSTEMIP')
        else:            
            for region in self.RegionsList:
                print 'Region {0}:uuid={1},locx={2},locy={3},port={4}'.format(region.name,str(region.uuid),region.locx,region.locy,region.port)
                cf.add_section(region.name)
                cf.set(region.name,'RegionUUID',str(region.uuid))
                cf.set(region.name,'Location',region.locx+','+region.locy)
                cf.set(region.name,'InternalAddress','0.0.0.0')
                cf.set(region.name,'InternalPort',region.port)
                cf.set(region.name,'AllowAlternatePorts','False')
                cf.set(region.name,'ExternalHostName','SYSTEMIP')
        fp=open(dst,'wb')
        cf.write(fp)
        fp.close()
    
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
    testdbParams={'dbProvider':"OpenSim.Data.MySQL.dll",'dbHost':'127.0.0.1','dbUser':'opensim','dbPsw':1234}
    #test RobustServer
    rs=RobustServer('Robust','./MainConfig.ini','127.0.0.1','E:/test/','E:/test/bin',testdbParams)
    rs.StartUp()
    #test OpenSimServer
    opensim=GridOpenSimServer('OpenSim0','./MainConfig.ini','127.0.0.1','E:/test/','E:/test/bin',testdbParams)
    opensim.StartUp()
    #opensim1=GridOpenSimServer('OpenSim1','./MainConfig.ini','127.0.0.1','E:/test/','E:/test/bin',testdbParams)
    #opensim1.StartUp()
    time.sleep(20)
    #testregionList=[]
    #testregion=Region('testregion,1065,1066,9066,testregion.tgz')
    #testregionList.append(testregion)
    #opensim.AddRegion(testregionList)
    #gridServerURL = 'http://127.0.0.1:9000'
    #gridServer = xmlrpclib.Server(gridServerURL)
    #gridServer.admin_create_user({'user_firstname':'test1', 'user_lastname':'test','user_password':'1234','start_region_x':128,'start_region_y':128})
    #gridServer.admin_create_region({'region_name':'sandbox','listen_ip':'0.0.0.0','listen_port':9068,'external_address':'SYSTEMIP','region_x':9068,'region_y':9069,'estate_name':'MyEstate'})