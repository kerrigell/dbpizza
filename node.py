#!/usr/bin/env python
#coding:utf-8
# Author:   Jianpo Ma
# Purpose:
# Created: 2013/6/17

import sys

from fabric.api import run,env,task,parallel,settings,hide
from fabric.utils import puts
from fabric.colors import *
from fabric.tasks import execute
from fabric.exceptions import NetworkError
from fabric.contrib.files import exists as fexists
import traceback
import uuid as muuid
import pdb
import string

reload(sys)
sys.setdefaultencoding('latin1')

from dbi import t_server
from dbi import session

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
            result=session.query(t_server).filter(t_server.pid==0).all()
        else:
            result=session.query(t_server).filter(t_server.id==dbid).all()
        return None if result is None or len(result) <> 1 else result[0]

    def add_child(self,child):
        if child is None or  not isinstance(child,Server):
            return False
        if self.childs is None:
            self.childs={}
        child.root=self.root
        child.level=self.level+1
        child.parent=self
        self.childs[child.dbid]=child

    def breed(self):
        '''依据自身.dbid值，繁殖子节点：返回子嗣数量'''
        if not (self.childs is None) and len(self.childs)>0:
            return len(self.childs)
        result=session.query(t_server).filter(t_server.pid==self.dbid).all()
        if result is None or len(result)==0:
            self.childs={}
            return 0
        for i in result:
            self.add_child(Server(i.id))
        return len(self.childs)

    def __getitem__(self,index):
        '''Get the item of the access way'''
        #print 'getitem_index: %s' % index
        try:
            for i in range(self.level-index):
                it=it.parent
            return it
        except Exception,e:
            self._print_error(e)

    def __str__(self):
        return "%s:%s:%s[%03d:%s]" % (self.s.region,self.s.product,self.s.ip_oper,self.dbid,self.s.description)

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

    def execute(self,cmd,hide_running=True,hide_stdout=True,hide_stderr=False,hide_output_prefix=False,hide_puts=False):
        try:
            if self.level >2:
                raise "Don't supply operation on 4 round"
            env.host_string ='%s@%s' % (self.s.loginuser,'127.0.0.1' if self.root == self else self.s.ip_oper)
            env.gateway = "%s@%s" % (self.parent.s.loginuser,self.parent.s.ip_oper) if self.level == 2 and self.parent != None else None
            hiding_clause = ( 'running' if hide_running else None, 'stdout' if hide_stdout else None, 'stderr' if hide_stderr else None)
            hiding_clause = [ x for x in hiding_clause if x ]
            with settings(hide(*hiding_clause),warn_only=True):
                #env.skip_bad_hosts=True
                env.connection_attempts=2
                env.disable_known_hosts=True
                env.eagerly_disconnect=True
                env.abort_on_prompts=True
                env.warn_only=True
                env.output_prefix=False if hide_output_prefix else False
                if hide_puts is True:
                    return run(cmd,shell=False)
                else:
                    return Server._print_result(run(cmd,shell=False),showprefix=False,info=str(self))
        except NetworkError,e:
            pdb.set_trace()
            traceback.print_exc()
           # print '%s Error: #%d %s' % (target.address, e.args[0], e.args[1])
          #  return ''
         #   puts('%s Error: #%d %s' % (target.address,e.args[0], e.args[1]))
            return 0
        except Exception,e:
            pdb.set_trace()
            traceback.print_exc()
         #   puts('%s Error: #%d %s' % (target.address,e.args[0], e.args[1]))
         #   print '%s Error: #%d %s' % (target.address, e.args[0], e.args[1])
            return 0

    @staticmethod
    def _print_result(result,hopevalue=None,showprefix=None,info=''):
        code=-99
        try:
            code=result.return_code
        except:
            pass
        if result.succeeded:
            if len(result):
                puts(yellow("%s ReturnCode:%s" % (info,result.return_code if code <> -99 else ''))
                            + green('\n' + result)
                            ,show_prefix=showprefix,flush=True)
                if hopevalue and result != hopevalue:
                    puts(red("The Result is not hope"),show_prefix=showprefix)
                    return 0
                return 1
        if result.failed:
            #result.return_code == 1
            puts(yellow("ReturnCode:%s" % result.return_code if code <> -99 else '')
                    + red('\n' + result)
                    ,show_prefix=showprefix,flush=True)
            return 0

    def infect_execute(self,cmd,extent=False):
        '''infect a file or command to childs or whole'''
        if self.childs is None:
            self.breed()
        for i in self.childs.values():
            i.execute(cmd)
            if extent:
                i.infect_execute(cmd,extent)


    def exists(self,path):
        env.host_string='%s@%s' % (self.s.loginuser,'127.0.0.1' if self.root ==self else self.s.ip_oper)
        env.gateway = self.parent.s.ip_oper if self.level == 2 and self.parent != None else None
        return fexists(path)

    def download(self,path,uuid=None):
        try:
            parent = self.parent
            local_ip = self.s.ip_oper
            if uuid == -1:
                return -1
            elif uuid is not None:
                if parent.exists("/tmp/%s" % uuid):
                    if parent.execute("scp -r /tmp/%s %s:/tmp/%s" % (uuid,local_ip,uuid),hide_stdout=False,hide_output_prefix=True,hide_puts=True):
                        puts(yellow("%s+-->%s"%(string.ljust(' ',self.level*4,),str(self))),show_prefix=False)
                        return uuid
                    else:
                        puts(red("%s+-->%s:%s"%(string.ljust(' ',self.level*4,),str(self),"Transfer Failed!")),show_prefix=False)
                        return -1
                else:
                    return self.download(path,uuid)
            else:
                if parent is None or parent.level == 0:
                    if parent.exists(path):
                        uuid = uuid if uuid else muuid.uuid1()
                        if parent.execute("scp -r %s %s:/tmp/%s" % (path,local_ip,uuid),hide_stdout=False,hide_output_prefix=True,hide_puts=True):
                            puts(yellow("%s+-->%s" % (string.ljust(' ',self.level*4),str(self))),show_prefix=False)
                            return uuid
                        else:
                            puts(red("%s+-->%s:%s" % (string.ljust(' ',self.level*4,),str(self),"Transfer Failed!")),show_prefix=False)
                            return -1
                    else:
                        puts(red("%s+-->%s:%s" % (string.ljust(' ',self.level*4,),str(self),"File not  exists")),show_prefix=False)
                        return -1
                else:
                    return self.download(path,parent.download(path))

        except Exception, e:
            traceback.print_exc()

    def infect_download(self,path,extent=False,uuid=None):
        '''infect a file or command to childs or whole'''
        if self.childs is None:
            self.breed()
        for i in self.childs.values():
            tuuid=i.download(path,uuid)
            if tuuid is not None and uuid is None and tuuid != -1:
                uuid=tuuid
            if extent and uuid and uuid <>-1:
                i.infect_download(path,uuid)

    def upload(self,local_path,uuid=None):
        pass

