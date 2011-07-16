#!/usr/bin/env python
#coding=utf-8
import ConfigParser

class CAppConfig(ConfigParser.ConfigParser):
    def setValue(self,section,option,value):    
        self.set(section,option,value)

    def getValue(self,section,option):
        try:
            value = self.get(section,option)
        except ConfigParser.NoOptionError:
            value = "<NoOption>"
        return value

    def optionxform(self,optionstr):
        return optionstr             

    def __init__(self,filename):
        ConfigParser.ConfigParser.__init__(self)
        self.filename=filename
        self.read(filename)

    def __del__(self):
	fp = open(self.filename,"w")
        self.write(fp)
	fp.close()
