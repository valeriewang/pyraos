#!/usr/bin/env python
#coding=utf-8
import 

class NetWorkError(Exception):
    def __init__(self,url):
        self.msg='wrong url {0},can\'t get access with it'.format(url)
        self.url=url

class ConfigParamsError(Exception):
    def __init__(self,section,attr):
        self.attr=attr
        self.sec=section
        self.msg='{0} in {1} is not set or has an empty value'.format(attr,section)

class DownLoadError(Exception):
    def __init__(self):
        self.msg='DownLoad Fail'