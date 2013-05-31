#!/usr/bin/env python
#coding:utf-8
# Author:  Jianpo Ma
# Purpose: 
# Created: 2013/3/29

from fabric.api import run,env,task,parallel,settings,hide
from fabric.utils import puts
from fabric.colors import *
from fabric.tasks import execute
from fabric.exceptions import NetworkError

from connection import conn
import sqlobject

class servers(sqlobject.SQLObject):
    _connection=conn
    pid=sqlobject.IntCol('pid',length=11,default=None)
    region=sqlobject.EnumCol(enumValues=['hk','vn','id','tw','th','us','my','cn','in',None],default=None)
    product=sqlobject.EnumCol(enumValues=['tlbb','ldj','taoyuan','guyu','totem','specialforce','gamefuse','oppaplay','gamiction','cuaban','davinci','swordgirls','common'],default=None)
    role=sqlobject.EnumCol(enumValues=['cc','backup','db',None],default=None)
    loginuser=sqlobject.StringCol(length=40,default='root')
    description=sqlobject.StringCol('description',length=250,default=None)
    ip_oper=sqlobject.StringCol(length=250,default=None)
    ip_private=sqlobject.StringCol(length=16,default=None)
    ip_public=sqlobject.StringCol(length=16,default=None)
    ip_ilo=sqlobject.StringCol(length=16,default=None)
    is_reserve=sqlobject.TinyIntCol(length=1,default=None)
    dbms=sqlobject.EnumCol(enumValues=['MySQL','Oracle','MSSQL'],default=None)
    vender=sqlobject.EnumCol(enumValues=['Dell','HP','VMware','Intel','Xen'],default=None)
    model=sqlobject.StringCol(length=250,default=None)
    os_type=sqlobject.EnumCol(enumValues=['Linux','Windows'],default=None)
    os_release=sqlobject.EnumCol(enumValues=['RHEL_5_3','RHEL_4_8','RHEL_4_6','CENT_6_3','WIN2003','WIN2008'],default=None)
    os_arch=sqlobject.EnumCol(enumValues=['x86_64','i386'],default=None)
    update_time=sqlobject.TimestampCol(default=None)
    create_time=sqlobject.TimestampCol(default=None)
    is_deleted=sqlobject.TinyIntCol(length=1,default=None)
    
########################################################################
class Server(object):
    """Server.s --->  sqlobject ---> TABLE:servers"""

    #----------------------------------------------------------------------
    def __init__(self,s=None,parent=None):
        """Constructor"""
        self.s=s if isinstance(s,servers) else None
        self.parent=parent if isinstance(parent,Server) else None
        self.childs={}
        self.root=None
        self.level=0
        self._iter_step=None
        self._iter_parent=None
        if isinstance(parent,Server):
            parent.add_child(self)
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
        return '%s[%s:%s]' % (self.s.ip_oper,self.s.description, '' if self.parent == None else self.parent.s.ip_oper)
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
    def add_child(self,child):
        def _set_child_root(start,root):
            for i in start.childs.values():
                i.root=root
                i.level=start.level+1
                _set_child_root(i,root)
        if not isinstance(child,Server):
            return -1
        if not self.childs.has_key(child.s.id):
            self.childs[child.s.id]=child
            child.parent=self
            child.level=self.level+1
            if self.root:
                child.root=self.root
                _set_child_root(child,self.root)
            else:
                child.root=self
                _set_child_root(child,self)
        return child.level        
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


class ServerT(object):
    """"""
    def __init__(self,address,whoami='',user='root',port=22,childs=None):
        self.dbid=None
        self._step=None
        self._parent=None
        self.address=address
        self.user=user
        self.port=port
        self.whoami=whoami
        self.level=0
        self.parent=None
        self.childs={}
        self.root=None
        self.q=None
        if childs:
            for i in childs:
                self.add_child(i)
                
    def __getitem__(self,index):
  #      print 'getitem_index: %s' % index
        try:
            it=self
            for i in range(self.level-index):
                it=it.parent
            return it
        except Exception,e:
            self._print_error(e)
    def __str__(self):
        return '%s[%s:%s]' % (self.address,self.whoami, '' if self.parent == None else self.parent.address)
    def __len__(self):
        return self.level
    def __iter__(self):
        self._step=self.level-1
        self._parent=self
        return self
    def next(self):
        if self._step < 0:
            self._step=self.level
            raise StopIteration
        self._parent=self._parent.parent
        self._step-=1
        return self._parent
    def _print_error(e):
        puts('%s Error: #%d %s' % (self.address, e.args[0], e.args[1]))
    def add_child(self,child):
        def _set_child_root(start,root):
            for i in start.childs.values():
                i.root=root
                i.level=start.level+1
                _set_child_root(i,root)
      #  if type(child) != type(Server):
      #      return None
        if not self.childs.has_key(child.address):
            self.childs[child.address]=child
            child.parent=self
            child.level=self.level+1
            if self.root:
                child.root=self.root
                _set_child_root(child,self.root)
            else:
                child.root=self
                _set_child_root(child,self)
        return child.level
        
    def search(self,addr):
        def _search(addr,start):
            if start.address == addr:
                return start
            if start.childs.has_key(addr):
                return start.childs[addr]
            for value in start.childs.values():
                result=_search(addr,value)
                if result:
                    return result
        root=self if (self.root == None) else self.root
        return _search(addr,root)
    def search_list(self,addr):
        def _search_list(addr,start,result):
            if start.address.find(addr) != -1:
                result.append(str(start.address))
            for tkey in start.childs.keys():
                if tkey.find(addr) != -1:
                    result.append(str(start.childs[tkey].address))
                for value in start.childs.values():
                    _search_list(addr,value,result)
        slist=[]
        root=self if (self.root == None) else self.root
        _search_list(addr,root,slist)
        return slist
    def walk(self,dest_addr,src_addr=None):
        #seach child
        return self._walk(self.search(src_addr) if src_addr else self,self.search(dest_addr))
    def _walk(self,src_server,dest_server):
        #seach child
        if src_server == None or dest_server == None:
            return []        
        start=[src_server] + [x for x in src_server] 
        end=[dest_server] +[x for x in dest_server]
        same=[x for x in start if x in end]
        result=start[:start.index(same[0])] +same[0:1]+ end[:end.index(same[0])][::-1]
     #   end=end.reverse()
        #tmp=start + end
        #result=sorted(set(tmp),key=tmp.index)
        return result        
    def run(self,cmd):
        def _run_from_root(target,cmd,host_string,gateway=None):
            if gateway:
                env.gateway=gateway
            #    print 'gateway:%s' % env.gateway
            env.host_string=host_string
            print env.host_string
            try:
                with settings(hide('running','stdout'),warn_ony=True):
                    env.skip_bad_hosts=True
                    env.connection_attempts=2
                    env.disable_known_hosts=True
                    env.eagerly_disconnect=True
                    env.abort_on_prompts=True
                    env.warn_only=True
                    return run(cmd,shell=False)
            except NetworkError,e:
                traceback.print_exc()
               # print '%s Error: #%d %s' % (target.address, e.args[0], e.args[1])
              #  return ''
             #   puts('%s Error: #%d %s' % (target.address,e.args[0], e.args[1]))
            except Exception,e:
                traceback.print_exc()
             #   puts('%s Error: #%d %s' % (target.address,e.args[0], e.args[1]))
             #   print '%s Error: #%d %s' % (target.address, e.args[0], e.args[1])
                return ''
       # print 'test ===> %s' % self.address
        if self.level >2:
            raise "Don't supply operation on 4 round"
        root= self if self.root == None else self.root
        host_string='%s@%s:%s' % (self.user,'127.0.0.1' if self.root == None else self.address,self.port)
        gateway= self.parent.address if self.level == 2 and self.parent != None else None
        return _run_from_root(self,cmd,host_string,gateway)
    def getfile(self,dest_server,dest_path,local_file,local_path):
        walkpath=self._walk(self,dest_server)
        if not walkpath:
            raise 'Send falut: because the way error'
        
    def putfile(self,local_file,dest_server,dest_path):
        import os.path
        (lpath,lfile) = os.path.split(local_file)
        #print lpath,lfile
        if not len(lfile):
            return False
        walkpath=self._walk(self,dest_server)
        if not walkpath:
            puts(red("Error: Not found the correct way from %s to %s" ))
            return
        tpath='/tmp'
        ltpath=None
        import random,string
        tmpfile=''.join(random.sample([chr(i) for i in range(97, 122)], 15))
        
        for (f,t) in map(None,walkpath,walkpath[1:]):
            print '%s --> %s' % ('' if f == None else f.address,'' if t == None else t.address)
            if t == None:
                f.run('mv %s/%s %s/%s' % (tpath,tmpfile,dest_path,lfile))
                print 'mv %s to %s' % (tmpfile, '%s/%s' % (dest_path, lfile))
                print 'send finished'
                break
            if f.level > t.level:
                cmd='scp  %s@%s:%s %s %s ' % (f.user, f.address, '%s/%s' % (ltpath if ltpath else lpath,tmpfile if ltpath else lfile),tpath, ' && rm -f %s' % ('%s/%s' % (tpath,tmpfile)) if  ltpath else '')
                print cmd
                t.run(cmd)
            else:
                cmd='scp  %s %s@%s:%s %s' % ( '%s/%s' % (ltpath if ltpath else lpath,tmpfile if ltpath else lfile),t.user, t.address,'%s/%s' %(tpath,tmpfile), ' && rm -f %s' % ('%s/%s' % (tpath,tmpfile)) if  ltpath else '')
                print cmd
                f.run(cmd)
            if not ltpath:
                ltpath=tpath
    def deploy(self):
        pass
    def infect(self,extent):
        '''infect a file or command to childs or whole'''
        pass



