#!/usr/bin/env python
#coding=utf-8

type='robust'
robustConfigDic={'ID':'myrobust',
                 'loc':'E:/test/2/robust',
                 'src':'E:/test/2/0.3.rar',
                 'dbProvider':'OpenSim.Data.MySQL.dll',
                 'connString':'Data Source=127.0.0.1;Database=robust;User ID=opensim;Password=1234;Old Guids=true;',
                 'listener_port':8003,
                 'login_port':8002,
                 'host':'http://127.0.0.1',
                 'DataCenter':'http://localhost'
                }
gridopensimDic0={'ID':'opensim0',
                'loc':'E:/test/2/opensim0',
                'src':'E:/test/2/0.3.rar',
                'dbProvider':'OpenSim.Data.MySQL.dll',
                'connString':'Data Source=127.0.0.1;Database=opensim0;User ID=opensim;Password=1234;Old Guids=true;',
                'listener_port':9100,
                'robusturl':'http://127.0.0.1:8003',
                'host':'http://127.0.0.1',
                'DataCenter':'http://localhost'
                }
gridopensimDic1={'ID':'opensim1',
                'loc':'E:/test/2/opensim1',
                'src':'E:/test/2/0.3.rar',
                'dbProvider':'OpenSim.Data.MySQL.dll',
                'connString':'Data Source=127.0.0.1;Database=opensim2;User ID=opensim;Password=1234;Old Guids=true;',
                'listener_port':9099,
                'robusturl':'http://127.0.0.1:8003',
                'host':'http://127.0.0.1',
                'DataCenter':'http://localhost'
                }
                
gridopensimDic2={'ID':'opensim2',
                'loc':'E:/test/2/opensim2',
                'src':'E:/test/2/0.3.rar',
                'dbProvider':'OpenSim.Data.MySQL.dll',
                'connString':'Data Source=127.0.0.1;Database=opensim2;User ID=opensim;Password=1234;Old Guids=true;',
                'listener_port':9098,
                'robusturl':'http://127.0.0.1:8003',
                'host':'http://127.0.0.1',
                'DataCenter':'http://localhost'
                }

gridDics=[girdopensimDic0,gridopensimDic1,gridopensimDic2]

opensimDic={'ID':'opensim',
            'loc':'E:/test/2/opensim',
            'src':'E:/test/2/0.3.rar',
            'dbProvider':'OpenSim.Data.MySQL.dll',
            'connString':'Data Source=127.0.0.1;Database=opensim;User ID=opensim;Password=1234;Old Guids=true;',
            'listener_port':9000,
            'host':'http://127.0.0.1',
            'DataCenter':'http://localhost'}



if __name__=='__main__':
    if(type=='robust'):
        if len(robustConfigDic)>0
            robustServer=RobustServer(robustConfigDic)
            robustServer.StartUp()
        for dic in girdDics:
            gridopensimServer=GridOpenSimServer(dic)
            gridopensimServer.StartUp()
    elif(type='standalone'):
        opensimServer=OpenSimServer(opensimDic)
        opensimServer.StartUp()
        
