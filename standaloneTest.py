#!/usr/bin/env python
#coding=utf-8
from GridManager import GridManager

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
    myGridManager=GridManager(configpath)
    myGridManager.CreateGrid('./gridconfig/gridA.ini')