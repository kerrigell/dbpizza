#!/usr/bin/env python
#coding:utf-8
# Author:   Jianpo Ma
# Purpose: 
# Created: 2013/6/17

import sys

from dbi import t_server
class Server(object):
    """Server.s --->  sqlobject ---> TABLE:servers"""
    def __init__(self,dbid=None):
        """Constructor"""
        self.s=self._get_dbinfo(dbid)
        self.dbid=None if self.s is None else self.s.id
        self.parent=None
        self.childs=None
        self.root=self
        self.level=0
        self._iter_step=None
        self._iter_parent=None
        
    @classmethod
    def _get_dbinfo(self,dbid):
        result=None
        if dbid is None:
            result=list(t_server.select(t_server.q.pid==0))
        else:
            result=list(t_server.select(t_server.q.id==dbid))
        return None if result is None or len(result) <> 1 else result[0]
    @classmethod
    def add_child(self,child):
        if not ( child and isinstance(child,Server)):
            return False
        if self.childs is None:
            self.childs={}
        child.root=self.root
        child.level=self.level+1
        child.parent=self
        self.childs[child.dbid]=child
        
    def breed(self):
        '''依据自身.dbid值，繁殖子节点：返回子嗣数量'''
        if not (self.childs is  None) and len(self.childs)>0:
            return len(self.childs)
        result=list(t_server.select(t_server.q.pid==self.dbid))
        if result is None or len(result)==0:
            return 0
        if self.childs is None:
            self.childs={}
        for i in result:
            self.add_child(Server(i.id))
        return len(self.childs)
    
    def __getitem__(self,index):
        '''Get the item of the access way'''
        #print 'getitem_index: %s' % index
        try:
            it=self
            for i in range(self.level-index):
                it=it.parent
            return it
        except Exception,e:
            self._print_error(e)        
    def __str__(self):
        return "%s:%s[%s]%s" % (self.dbid,self.s.ip_oper,self.s.description, '' if self.parent == None else "<%s" % self.parent.s.ip_oper)
    def __len__(self):
        return self.level
    def __iter__(self):
        self._iter_step=self.level-1
        self._iter_parent=self
        return self
    def next(self):
        if self._iter_step < 0:
            self._iter_step=self.level
            raise StopIteration
        self._iter_parent=self._iter_parent.parent
        self._iter_step-=1
        return self._iter_parent
    def _print_error(e):
        puts('%s Error: #%d %s' % (self.s.ip_oper, e.args[0], e.args[1]))             
    def search(self,addr):
        def _search(addr,start):
            if start.s.ip_oper == addr:
                return start
            for value in start.childs.values():
                result=_search(addr,value)
                if result:
                    return result
        root=self if (self.root == None) else self.root
        return _search(addr,root)    