#!/usr/bin/env python
#coding=utf-8
from threading import Thread
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import ReadConfig

class GridManager:
    def __init__(self,configpath):
        self.ParseConfig(configpath)
    def ParseConfig(self,path):
        cf=ReadConfig.CAppConfig(path)
        self.name=cf.get('gridmanager','name')
        self.grid_listener_port=cf.get('gridmanager','grid_listener_port')
        self.node_listener_port=cf.get('gridmanager','node_listener_port')
    def Start(self):
        Thread(target=self.grid_server_on_port,args=[self.grid_listener_port]).start()
        Thread(target=self.node_server_on_port,args=[self.node_listener_port]).start()
    def grid_server_on_port(self,port):
        server = ThreadingHTTPServer(("localhost",int(port)), GridHandler)
        server.serve_forever()
    def node_server_on_port(self,port):
        server = ThreadingHTTPServer(("localhost",int(port)), NodeHandler)
        server.serve_forever()
    def CreateGrid(configpath):
        mygrid=Grid(configpath)
        mygrid.BuildServer()
    
class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class GridHandler(BaseHTTPRequestHandler):
    def do_POST(self):

        
        if self.path=="/CreateGrid/":
            AddGrid(ConfigPath)
        elif self.path=='/ShowGrid/':
            ShowGrid()
        print self.path, self.command,self.client_address
        if self.rfile:
            data=self.rfile.read()
        else:
            print 'no data'
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write("Grid Server")
    def AddGrid(self):
        pass
    def ShowGrid(self):
        pass
        
class NodeHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        print self.path,self.command
        print self.rfile;
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write("Node Server")


if __name__=='__main__':
    myGridManager=GridManager('./MainConfig.ini')
    myGridManager.Start()
