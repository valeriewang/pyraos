#!/usr/bin/env python
#coding=utf-8
import subprocess
import time

port=8080
configpath='./GridManager.ini'
subprocess.Popen(["start python GridManager.py {0} {1}".format(port,configpath)],cwd='E:/virtualpku/pyRAOS/',shell=True)
print 'startup gridmanager'
port=8071
configpath='./nodeserver1.ini'
subprocess.Popen(["start python Node.py {0} {1}".format(port,configpath)],cwd='E:/virtualpku/pyRAOS/',shell=True)
print 'startup nodeserver1'
port=8072
configpath='./nodeserver2.ini'
subprocess.Popen(["start python Node.py {0} {1}".format(port,configpath)],cwd='E:/virtualpku/pyRAOS/',shell=True)
print 'startup nodeserver2'
port=8073
configpath='./nodeserver3.ini'
subprocess.Popen(["start python Node.py {0} {1}".format(port,configpath)],cwd='E:/virtualpku/pyRAOS/',shell=True)
print 'startup nodeserver3'