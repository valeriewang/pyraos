#!/usr/bin/env python
#coding=utf-8

import httplib, mimetypes

def post_multipart(host, selector, fields, files):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    body1="Method=CreateGrid,ConfigFile=configfile"
    content_type1="content_type:plain/html"
    h = httplib.HTTP(host)
    h.putrequest('POST', selector)
    h.putheader('content-type', content_type1)
    h.putheader('content-length', str(len(body1)))
    h.endheaders()
    h.send(body1)
    errcode, errmsg, headers = h.getreply()
    return h.file.read()


if __name__=='__main__':
    fp=open('./MainConfig.ini')
    value=fp.read()
    post_multipart("127.0.0.1:8080","/",[("Method","CreateGrid")],[("Config","MainConfig.ini",value)])
