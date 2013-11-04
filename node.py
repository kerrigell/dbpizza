#!/usr/bin/env python
#coding:utf-8
# Author:   Jianpo Ma
# Purpose:
# Created: 2013/6/17

import sys

from fabric.api import run,env,task,parallel,settings,hide,open_shell
from fabric.utils import puts
from fabric.colors import *
from fabric.tasks import execute
from fabric.exceptions import NetworkError
from fabric.contrib.files import exists as fexists
import traceback
import uuid as muuid
import pdb
import string
import ConfigParser
import os.path

reload(sys)
sys.setdefaultencoding('latin1')

########################################################################
class NodeNet(object):
    """"""
    # the node that watched by someone on this net
    current_node=None
    # db table class
    __dbclass__=None
    # db session
    __dbsession__=None
    # the map of objects
    __nodemap__={}
    # foreign class
    __foreignclass__=None
    # foreign node
    foreignnode=None
    #----------------------------------------------------------------------
    @classmethod
    def _get_dbclass(cls):
        if cls.__dbsession__ and cls.__dbclass__:
            return True
        selfclassname=cls.__name__
        dbclassname="t_%s" % string.lower(selfclassname)
        dbclass=None
        dbsession=None        
        import importlib
        mo=importlib.import_module('dbi')
        if mo:
            if hasattr(mo,dbclassname):
                dbclass= getattr(mo,dbclassname)
            if hasattr(mo,'session'):
                dbsession=getattr(mo,'session')
            if dbclass and dbsession:
                cls.__dbsession__=dbsession
                cls.__dbclass__=dbclass
                return True
            else:
                return False
    @classmethod
    def _get_dbinfo(cls,dbid):
        if not cls._get_dbclass():
            return None
        if cls.__nodemap__.has_key(dbid) and cls.__nodemap__[dbid].s is not None:
            return cls.__nodemap__[dbid].s
        result=None
        
        if dbid is None:
            result=cls.__dbsession__.query(cls.__dbclass__).filter(cls.__dbclass__.pid==0).all()
        else:
            result=cls.__dbsession__.query(cls.__dbclass__).filter(cls.__dbclass__.id==dbid).all()
        return None if result is None or len(result) <> 1 else result[0]
    def dockapply(self):
        result=False
        if self.s is None or self.__dbclass__ is None or  self.__foreignclass__ is None or self.__dbclass__ is None or not hasattr(self.__dbclass__ , string.lower("%s_id" % self.__foreignclass__.__name__)):
            return result
        foreignid=getattr(self.s, string.lower("%s_id" % self.__foreignclass__.__name__))
        if foreignid:
            self.__foreignclass__.dockhandle(self,foreignid)
    @classmethod
    def dockhandle(cls,applicant,searchid):
        the_node=cls.get_node(searchid)
        if the_node is None:
            return False
        else:
            the_node.foreignnode=applicant
            applicant.foreignnode=the_node
    def __init__(self,dbid,foreignclass=None):
        """Constructor"""
        self.__foreignclass__=foreignclass
        if self.__class__.__dbsession__ is None  or self.__class__.__dbclass__ is None:
            self._get_dbclass()
        # 需要重载赋值，实现从已有map中恢复实例
        #if self.__class__.__nodemap__.has_key(dbid) and isinstance(self.__class__.__nodemap__[dbid],self.__class__):
            #self=self.__class__.__nodemap__[dbid]
            #return
        self.s=self._get_dbinfo(dbid)
        self.dbid=None if self.s is None else self.s.id
        self.parent=None
        self.childs=None
        self.root=self
        self.level=0
        self._iter_step=None
        self._iter_parent=None
        if self.dbid is not None and not self.__class__.__nodemap__.has_key(self.dbid):
            self.__class__.__nodemap__[self.dbid]=self
        if self.__foreignclass__:
            self.dockapply()
        if self.__class__.current_node is None:
            self.__class__.current_node=self
    @classmethod
    def cd(cls,dbid):
        dbid=string.strip(dbid)
        cnode=cls.current_node
        if dbid == '.':
            cnode=cls.current_node
        elif dbid == '..':
            if cls.current_node.parent is not None:
                cnode=cls.current_node.parent
        else:
            cdbid=int(dbid)
            if cdbid is None or cdbid ==0:
                return cls.current_node
            else:
                if cdbid is not None and cdbid != 0 and cls.current_node.childs.has_key(cdbid):
                    cnode=cls.current_node.childs[cdbid]
        if cnode.childs is None:
            cnode.breed()
        cls.current_node=cnode
        return cls.current_node

        
    
    def add_child(self,child):
        if child is None or  not isinstance(child,self.__class__):
            return False
        if self.childs is None:
            self.childs={}
        child.root=self.root
        child.level=self.level+1
        child.parent=self
        self.childs[child.dbid]=child        
    def breed(self,recursion=False):
        '''依据自身.dbid值，繁殖子节点：返回子嗣数量'''
        child_count=0
        if not (self.childs is None) and len(self.childs)>0:
            child_count=len(self.childs)
            return child_count
        result=self.__dbsession__.query(self.__dbclass__).filter(self.__dbclass__.pid==self.dbid).all()
        if result is None or len(result)==0:
            self.childs={}
            return 0
        for i in result:
            child_node=self.__class__(i.id,self.__foreignclass__)
            self.add_child(child_node)
            child_count+=1
            if recursion:
                child_count+=child_node.breed(recursion)
        return len(self.childs)   
    @classmethod
    def get_node(cls,fdbid):
        if cls.__nodemap__.has_key(fdbid):
            return cls.__nodemap__[fdbid]
        dbinfo=cls._get_dbinfo(fdbid)
        if dbinfo is None:
            return None
        parent_node=cls.get_node(dbinfo.pid)
        if dbinfo.pid !=0 and parent_node is None:
            return None
        self_node=cls(fdbid,cls.__foreignclass__)
        if dbinfo.pid !=0:
            parent_node.add_child(self_node)
        return self_node
    def print_structure(self):
        print "%s+-%s" % (string.ljust('',self.level*4),self)
        if self.childs:
            for i in self.childs.values():
                i.print_structure()

            
class Feature(NodeNet):
    """"""
    __nodemap__={}
    current_node=None
    def __init__(self,dbid=None,foreignclass=None):
        super(Feature,self).__init__(dbid,foreignclass)
    def __str__(self):
        return "<%s:%s>" % (self.s.feature,self.s.detail)
    def print_structure(self):
        print "%s+-%s" % (string.ljust('',self.level*4),"%s---%s->%s" %(self,self.foreignnode.__class__.__name__,self.foreignnode) if self.foreignnode else self)
        for i in self.childs.values():
            i.print_structure()
    def __str__(self):
        if self.s is None:
            return 'None'
        return ("%s[%s:%s]%s" % ( self.s.detail,self.dbid, '' if self.parent is None else self.parent.s.detail, '' if self.foreignnode is None else "-->%s" %self.foreignnode)).encode('gbk')
class Server(NodeNet):
    """Server.s --->  sqlobject ---> TABLE:servers"""
    __nodemap__={}
    current_node=None
    def __init__(self,dbid=None,foreignclass=None):
        """Constructor"""
        super(Server,self).__init__(dbid,foreignclass)


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
        return ("%s:%s:%s[%03d:%s]" % (self.s.region,self.s.product,self.s.ip_oper,self.dbid,self.s.description)).encode('gbk')

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
    def job(self,ffile,task,*args):
            #,hide_running=True,hide_stdout=True,hide_stderr=False,hide_output_prefix=False,hide_puts=False):
        try:
            if self.level >2:
                raise "Don't supply operation on 4 round"
            env.host_string ='%s@%s' % (self.s.loginuser,'127.0.0.1' if self.root == self else self.s.ip_oper)
            env.gateway = "%s@%s" % (self.parent.s.loginuser,self.parent.s.ip_oper) if self.level == 2 and self.parent != None else None
            hiding_clause = ( 'running' if hide_running else None, 'stdout' if hide_stdout else None, 'stderr' if hide_stderr else None)
            hiding_clause = [ x for x in hiding_clause if x ]
            with settings(hide('running','stdout','stderr'),warn_only=True):  #*hiding_clause),warn_only=True):
                env.skip_bad_hosts=True
                env.connection_attempts=2
                env.disable_known_hosts=True
                env.eagerly_disconnect=True
                env.abort_on_prompts=True
                env.warn_only=True
                env.output_prefix=False
                result=execute(task,*args)
                print result
        except NetworkError,e:
            puts(red("Error: %s \n #%s" % (host_string,e)))
            return 0
        except Exception,e:
            puts(red("Error: %s \n #%s" % (host_string,e)))
            return 0
    def execute(self,cmd,hide_running=True,hide_stdout=True,hide_stderr=False,hide_output_prefix=False,hide_puts=False,showprefix=None):
        class ExecuteOut(object):
            def __init__(self):
                self.return_code=-99
                self.result=''
                self.succeed=False
        out=ExecuteOut()
        out.return_code=-99
        out.result=''
        out.succeed=False
        host_string='%s@%s' % (self.s.loginuser,'127.0.0.1' if self.root == self else self.s.ip_oper)
        gateway_string="%s@%s" % (self.parent.s.loginuser,self.parent.s.ip_oper) if self.level == 2 and self.parent != None else None
        try:
            if self.level >2:
                raise "Don't supply operation on 4 round"
            env.host_string =host_string
            env.gateway = gateway_string
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
                result= run(cmd,shell=False)
                out.result=str(result)
                if hasattr(result,'return_code'):
                    out.return_code=result.return_code                
                if not hide_puts:
                    puts(yellow("%s ReturnCode:%s" % (str(self),result.return_code if hasattr(result,'return_code') else '')),show_prefix=showprefix,flush=True)
                if result.succeeded:
                    if not hide_puts:
                        puts(green(result),show_prefix=showprefix,flush=True)
                    out.succeed=True
                if result.failed:
                    out.succeed=False
                    if not hide_puts:
                        puts(red(result),show_prefix=showprefix,flush=True)
            return out
        except NetworkError,e:
          #  traceback.print_exc()
           # print '%s Error: #%d %s' % (target.address, e.args[0], e.args[1])
          #  return ''
            out.succeed=False
            out.result="Error: %s \n #%s" % (host_string,e)
            if not hide_puts:
                puts(red(out.result))
            return out
        except Exception,e:
          #  traceback.print_exc()
            out.succeed=False
            out.result="Error: %s \n #%s" % (host_string,e)
            if not hide_puts:
                puts(red(out.result))
            return out
         #   print '%s Error: #%d %s' % (target.address, e.args[0], e.args[1])

    def login(self,cmd=None,hide_running=True,hide_stdout=True,hide_stderr=False,hide_output_prefix=False,hide_puts=False):
        host_string='%s@%s' % (self.s.loginuser,'127.0.0.1' if self.root == self else self.s.ip_oper)
        gateway_string="%s@%s" % (self.parent.s.loginuser,self.parent.s.ip_oper) if self.level == 2 and self.parent != None else None
        try:
            if self.level >2:
                raise "Don't supply operation on 4 round"
            env.host_string =host_string
            env.gateway = gateway_string
            hiding_clause = ( 'running' if hide_running else None, 'stdout' if hide_stdout else None, 'stderr' if hide_stderr else None)
            hiding_clause = [ x for x in hiding_clause if x ]
            with settings(hide(*hiding_clause),warn_only=True):
                #env.skip_bad_hosts=True
                env.connection_attempts=2
                #env.disable_known_hosts=True
                #env.eagerly_disconnect=True
                env.abort_on_prompts=True
                #env.warn_only=True
                env.output_prefix=False if hide_output_prefix else False
                open_shell(cmd)

        except NetworkError,e:
            #pdb.set_trace()
            #traceback.print_exc()
           # print '%s Error: #%d %s' % (target.address, e.args[0], e.args[1])
          #  return ''
         #   puts('%s Error: #%d %s' % (target.address,e.args[0], e.args[1]))
            puts(red("Error: %s \n #%s" % (host_string,e)))
            return 0
        except Exception,e:
            #pdb.set_trace()
            #traceback.print_exc()
         #   puts('%s Error: #%d %s' % (target.address,e.args[0], e.args[1]))
         #   print '%s Error: #%d %s' % (target.address, e.args[0], e.args[1])
            puts(red("Error: %s \n #%s" % (host_string,e)))
            return 0
        
    @staticmethod
    def _print_result(result,showprefix=None,info=''):
        puts(yellow("%s ReturnCode:%s" % (info,result.return_code if hasattr(result,'return_code') else '')),show_prefix=showprefix,flush=True)
        if result.succeeded:
            puts(green(result),showprefix=showprefix,flush=True)
        if result.failed:
            puts(yellow(red(result),show_prefix=showprefix,flush=True))

    #def infect_execute(self,cmd,extent=False):
        #'''infect a file or command to childs or whole'''
        #if self.childs is None:
            #self.breed()
        #for i in self.childs.values():
            #i.execute(cmd)
            #if extent:
                #i.infect_execute(cmd,extent)


    def exists(self,path):
        env.host_string='%s@%s' % (self.s.loginuser,'127.0.0.1' if self.root ==self else self.s.ip_oper)
        env.gateway = self.parent.s.ip_oper if self.level == 2 and self.parent != None else None
        return fexists(path)

    def download(self,path,uuid=None,targetpath='/tmp'):
        try:
            filename = [ x for x in path.split('/') if x ][-1] 
            parent = self.parent
            local_ip = self.s.ip_oper
            local_user=self.s.loginuser
            if uuid == -1:
                return -1
            elif uuid is not None:
                if parent.exists("/tmp/%s" % uuid):
                    puts(yellow("%s+-->%s"%(string.ljust(' ',self.level*4,),str(self))),show_prefix=False)
                    if parent.execute("scp -r /tmp/%s %s@%s:/tmp/%s" % (uuid,local_user,local_ip,uuid),hide_stdout=False,hide_output_prefix=True,hide_puts=True).succeed:
                        if not self.exists(targetpath):
                            self.execute("mkdir -p %s" %(targetpath),hide_stdout=False,hide_output_prefix=True,hide_puts=True)
                        self.execute("cp -r /tmp/%s %s/%s" %(uuid, targetpath,filename),hide_stdout=False,hide_output_prefix=True,hide_puts=True)
                        return uuid
                    else:
                        puts(red("%s+-->%s:%s"%(string.ljust(' ',self.level*4,),str(self),"Transfer Failed!")),show_prefix=False)
                        return -1
                else:
                    return self.download(path,uuid)
            else:
                if parent.level == 0:
                    if parent.exists(path):
                        uuid = uuid if uuid else muuid.uuid1()
                        parent.execute("cp -r %s /tmp/%s" % (path, uuid), hide_stdout=False,hide_output_prefix=True,hide_puts=True)
                        puts(yellow("%s+-->%s" % (string.ljust(' ',self.level*4),str(self))),show_prefix=False)
                        if parent.execute("scp -r /tmp/%s %s@%s:/tmp/%s" % (uuid,local_user,local_ip,uuid),hide_stdout=False,hide_output_prefix=True,hide_puts=True).succeed:
                          #  if not self.exists(targetpath):
                          #      self.execute("mkdir -p %s" %(targetpath),hide_stdout=False,hide_output_prefix=True,hide_puts=True)                            
                          #  self.execute("cp -r  /tmp/%s %s/%s" %(uuid, targetpath,filename),hide_stdout=False,hide_output_prefix=True,hide_puts=True)
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
    @classmethod
    def piece(cls,line):
        if cls.__dbclass__ is None:
            return None
        dbids=cls.__dbclass__.piece(line)
        serverlist=[]
        for i in dbids:
            tnode=cls.get_node(i)
            if tnode:
                serverlist.append(tnode)
        return serverlist
    def add_child_info(self,ip_oper,description,region,loginuser='root'):
        dbsession=self.__class__.__dbsession__
        dbclass=self.__class__.__dbclass__
        dbsession.add(dbclass(pid=self.dbid,
                              ip_oper=ip_oper,
                              description=description,
                              region=region,
                              product=product,
                              role=role,
                              loginuser=loginuser
                            ))
        dbsession.commit()
                    
    def sendto(self,local_file,dest_server,dest_path,uuid=None):
        import os.path
        (lpath,lfile) = os.path.split(local_file)

        if not len(lfile):
            return None
        walkpath=self.walk(self,dest_server)
        if not walkpath:
            puts(red("Error: Not found the correct way from %s to %s" ))
            return None
        tpath='/tmp'
        ltpath=None
        
        if uuid is None:
            uuid=muuid.uuid1()
        tmpfile=uuid
        
        puts(yellow("%s+-->%s"%(string.ljust(' ',self.level*4,),str(self))),show_prefix=False)
        
        for (f,t) in map(None,walkpath,walkpath[1:]):
            puts(yellow("%s+-->%s"%(string.ljust(' ',f.level*4,)+str(f),str(t))),show_prefix=False)
            if t == None:
                #parent.execute("scp -r /tmp/%s %s@%s:/tmp/%s" % (uuid,local_user,local_ip,uuid),hide_stdout=False,hide_output_prefix=True,hide_puts=True).succeed
                if f.execute('mv %s/%s %s/%s' % (tpath
                                              ,tmpfile,
                                              dest_path,
                                              lfile)
                             ,hide_stdout=False,hide_output_prefix=True,hide_puts=True).succeed:
                    print 'send finished'
                else:
                    print 'send failure'
                break
            if f.level > t.level:
                cmd='scp -r %s@%s:%s %s' % (f.s.loginuser
                                                , f.s.ip_oper
                                                ,'%s/%s' % (ltpath if ltpath else lpath,tmpfile if ltpath else lfile)
                                                ,'%s/%s' % (tpath,tmpfile)
                                        #        ,' && rm -f %s' % ('%s/%s' % (tpath,tmpfile)) if  ltpath else '')
                                        )
                print cmd
                
                t.execute(cmd,hide_stdout=False,hide_output_prefix=True,hide_puts=True)
            else:
                cmd='scp -r %s %s@%s:%s' % ( '%s/%s' % (ltpath if ltpath else lpath,tmpfile if ltpath else lfile)
                                                ,t.s.loginuser
                                                ,t.s.ip_oper
                                                ,'%s/%s' %(tpath,tmpfile)
                                           #     ,' && rm -f %s' % ('%s/%s' % (tpath,tmpfile)) if  ltpath else '')
                                           )
                print cmd
                f.execute(cmd,hide_stdout=False,hide_output_prefix=True,hide_puts=True)
            if not ltpath:
                ltpath=tpath
    @classmethod     
    def walk(cls,source_server,dest_server):
        #seach child
        if source_server is None or dest_server is None or type(source_server) != cls or type(dest_server) !=cls:
            return []        
        start=[source_server] + [x for x in source_server] 
        end=[dest_server] +[x for x in dest_server]
        same=[x for x in start if x in end]
        result=start[:start.index(same[0])] +same[0:1]+ end[:end.index(same[0])][::-1]
        #   end=end.reverse()
        #tmp=start + end
        #result=sorted(set(tmp),key=tmp.index)
        return result          
class IPsec(object):
    # db table class
    __dbclass__=None
    # db session
    __dbsession__=None

    #----------------------------------------------------------------------
    @classmethod
    def _get_dbclass(cls):
        if cls.__dbsession__ and cls.__dbclass__:
            return True
        selfclassname=cls.__name__
        dbclassname="t_%s" % string.lower(selfclassname)
        dbclass=None
        dbsession=None        
        import importlib
        mo=importlib.import_module('dbi')
        if mo:
            if hasattr(mo,dbclassname):
                dbclass= getattr(mo,dbclassname)
            if hasattr(mo,'session'):
                dbsession=getattr(mo,'session')
            if dbclass and dbsession:
                cls.__dbsession__=dbsession
                cls.__dbclass__=dbclass
                return True
            else:
                return False
    @classmethod
    def _get_dbinfo(cls,dbid=None):
        if not cls._get_dbclass():
            return None
        result=None
        
        if dbid is not None:
            result=cls.__dbsession__.query(cls.__dbclass__).filter(cls.__dbclass__.server_id==dbid).all()
        return result
    def __init__(self,srv):
        if srv is None:raise "Server Is Null"
        if type(srv) != Server: 
            raise "param type is not Server"
        self.server=srv
        if self.__class__.__dbsession__ is None  or self.__class__.__dbclass__ is None:
            self._get_dbclass()
        # 需要重载赋值，实现从已有map中恢复实例
        #if self.__class__.__nodemap__.has_key(dbid) and isinstance(self.__class__.__nodemap__[dbid],self.__class__):
            #self=self.__class__.__nodemap__[dbid]
            #return
        #self.s=self._get_dbinfo(self.server.dbid) 
    def add_filter(self,protocal,source_addr,dport,description,status=0,chain='INPUT'):
        dbsession=self.__class__.__dbsession__
        dbclass=self.__class__.__dbclass__
        dbsession.add(dbclass(server_id=self.server.dbid,
                                                                    protocal=protocal,
                                                                    source_addr=source_addr,
                                                                    dport=dport,
                                                                    description=description,
                                                                    status=status,
                                                                    chain=chain)
                                         )
        dbsession.commit()
    def del_filter(self,dbid):
        dbsession=self.__class__.__dbsession__
        dbclass=self.__class__.__dbclass__
        for instance in dbsession.query(dbclass).filter_by(id = dbid):
            dbsession.delete(instance)
        dbsession.commit()        
    def list(self):
        return self.__class__._get_dbinfo(self.server.dbid)      
    def make_script(self):
        ripsec=self.list()
        filterlist=''
        if self.server.parent is not None :
            parent_iplist=[]
            parent_iplist.append(self.server.parent.s.ip_public)
            parent_iplist.append(self.server.parent.s.ip_private)
            parent_iplist.append(self.server.parent.s.ip_oper)
            parent_iplist=[ i for i in parent_iplist if i ]
            parent_iplist=list(set(parent_iplist))

            for item in parent_iplist:
                filterlist += '''$IPTABLES -I INPUT -s %s -p tcp --dport 22 -j ACCEPT #cc:%s\n''' % (item,self.server.parent)

        for i in ripsec:
            filterlist += '''$IPTABLES -I %s -s %s -p %s -m multiport --dport %s -j ACCEPT #%s\n''' % (i.chain,i.source_addr,i.protocal,i.dport,i.description)

            
        ipsec_temp='''
IPTABLES=/sbin/iptables;
$IPTABLES -F;
$IPTABLES -Z;
$IPTABLES -X;

$IPTABLES -t mangle -F;
$IPTABLES -t mangle -Z;
$IPTABLES -t mangle -X;


$IPTABLES -P INPUT  ACCEPT;

$IPTABLES -I INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT;
$IPTABLES -I OUTPUT -m state --state NEW,ESTABLISHED,RELATED -j ACCEPT ;

%s

$IPTABLES -I INPUT -s 127.0.0.1 -j ACCEPT;
$IPTABLES -P INPUT  DROP;
$IPTABLES -P FORWARD DROP ;
$IPTABLES -P OUTPUT ACCEPT ;
service iptables save
    
    ''' % filterlist
        return ipsec_temp  
    def reload(self):
        self.server.execute(self.make_script())
class Monitor(object):
    config=None
    def __init__(self,srv):
        if srv is None:raise "Server Is Null"
        if type(srv) != Server: 
            raise "param type is not Server"
        self.server=srv
        self.ip_monitor=self.server.s.ip_monitor
        if self.config is None:
            self.config=ConfigParser.SafeConfigParser()
            self.config.read("config/monitor.ini")
        self.status={}

    def title(self):
        print str(self.server)
    def check(self,output=True):
        scripts = self.config.options('script')
        script_shell = ""
        for script in scripts:
            script_shell += """
                echo -n "is_installed_%s:";
                test -x /usr/local/nagios/libexec/%s \
                && echo True || echo False;
                """ % (script, script)
        shell="""
            %s

            echo -n "is_installed_Linux_pm:"
            INC=`perl -e 'print \"@INC\"'`;
            find ${INC} -name 'Linux.pm' -print 2> /dev/null \
            | grep -q 'Linux.pm' && echo True || echo False;
            
            echo -n "is_installed_nagios_plugin:";
            test -d /usr/local/nagios/libexec && echo True || echo False;

            echo -n "is_installed_nrpe:";
            test -d /usr/local/nagios/etc && echo True || echo False;

            echo -n "is_installed_utils_pm:";
            test -e /usr/local/nagios/libexec/utils.pm \
            && echo True || echo False;

            echo -n "version_perl:";
            perl -v |  egrep v[0-9\.]+ -o

            echo -n "is_ping_opened:";
            /sbin/iptables -nvL | grep icmp | grep -q '0.0.0.0\|%s' &>/dev/null\
            && echo True || echo False

            echo -n "is_5666_opened:";
            /sbin/iptables -nvL | grep 5666 | grep -q '%s' &>/dev/null\
            && echo True || echo False

            echo -n "is_configured_nrpe:";
            grep -q '%s' /etc/xinetd.d/nrpe &>/dev/null \
            && echo True || echo False
            
            echo -n "is_openssl_devel:";
            rpm  -qa | grep openssl-devel &>/dev/null \
            && echo True || echo False            
            """ % (script_shell, self.ip_monitor, self.ip_monitor, self.ip_monitor)
        raw_status=self.server.execute(shell,hide_puts=True)
        if raw_status.succeed:
            self.status = dict([ x.split()[0].split(':') for x in raw_status.result.split('\n') if x ])
            if output:
                self.title()
                names=self.status.keys()
                names.sort()
                for name in names:
                    print '%-40s    %s' % (name, self.status[name])  
    def upgrade_perl(self):
        if len(self.status) == 0:
            self.check(output=False)
        base_dir = self.config.get('basic', 'base_dir')
        file_name = self.config.get('tools', 'perl')
        file = base_dir + "/client/tools/" + file_name
        print file
        UUID = None
        if self.status['version_perl'] == 'v5.8.5':
            UUID = self.server.download(file, uuid=UUID)
            self.server.execute("""
                    cd /tmp/ && \
                    tar zxf perl-5.8.9.tar.gz && \
                    cd perl-5.8.9 && \
                    ./Configure -de &> /dev/null && \
                    make &> /dev/null && \
                    make test &> /dev/null && \
                    make install &> /dev/null
                    """,hide_puts=True)
    

    def config_iptables(self):
        if len(self.status) == 0:
            self.check(output=False)        
        self.title()
        if self.status['is_ping_opened'] == 'False':
            self.server.execute("""
                    /sbin/iptables -I INPUT -s %s -p icmp -j ACCEPT
                    """ % self.ip_monitor,hide_puts=True)
        if self.status['is_5666_opened'] == 'False':
            self.server.execute("""
                    /sbin/iptables -I INPUT -s %s -p tcp --dport 5666 -j ACCEPT
                    """ % self.ip_monitor,hide_puts=True)

    def deploy_script(self):
        if len(self.status) == 0:
            self.check(output=False)        
        base_dir = self.config.get('basic', 'base_dir')
        scripts = self.config.options('script')
        for script in scripts:
            UUID = None
            file_name = self.config.get('script', script)
            file = base_dir + "/client/libexec/" + file_name
            AP = "\/usr\/local\/nagios\/libexec\/%s" % file_name
            OP = "/usr/local/nagios/libexec/%s" % file_name
            if self.status['is_installed_%s' % script] == 'False':
                UUID = self.server.download(file, uuid=UUID)
                self.server.execute("""
                        mv /tmp/%s /usr/local/nagios/libexec/ &&
                        chmod +x /usr/local/nagios/libexec/%s;
                        grep -q nagios /etc/sudoers && \
                        (grep %s /etc/sudoers &> /dev/null \
                        || sed -i '/nagios/s/$/,%s/g' /etc/sudoers) \
                        || echo \"nagios ALL=NOPASSWD: %s\" \
                        >> /etc/sudoers
                        """ % (file_name, file_name, AP, AP, OP) ,hide_puts=True)
        self.title()
        self.server.execute("""
                sed -i \
                's/^Defaults    requiretty/#Defaults    requiretty/g'\
                /etc/sudoers
                """,hide_puts=True)

    def install_tools(self):
        if len(self.status) == 0:
            self.check(output=False)        
        base_dir = self.config.get('basic', 'base_dir')
        self.title()
        
        # Install Sys-Statistics-Linux
        if self.status['is_installed_Linux_pm'] == 'False':
            UUID = None
            file_name = self.config.get('tools', 'Linux_pm')
            file = base_dir + "/client/tools/" + file_name          
            UUID = self.server.download(file, uuid=UUID)
            self.server.execute("""
                    cd /tmp && \
                    tar zxf Sys-Statistics-Linux-0.66.tar.gz && \
                    cd Sys-Statistics-Linux-0.66 && \
                    perl Makefile.PL &> /dev/null; \
                    make &> /dev/null && \
                    make test &> /dev/null && make install &> /dev/null
                    """)

        # create user: nagios
        self.server.execute("""
                chattr -i /etc/shadow /etc/passwd; \
                groupadd nagios; \
                useradd -M -s /sbin/nologin nagios -g nagios; \
                mkdir -p /usr/local/nagios/libexec/;
                """)

        # Install nagios-plugins
        if self.status['is_installed_nagios_plugin'] == 'False':
            UUID = None
            file_name = self.config.get('tools', 'nagios_plugin')
            file = base_dir + "/client/tools/" + file_name            
            UUID = server.download(file, uuid=UUID)
            self.server.execute("""
                cd /tmp && \
                tar zxf nagios-plugins-1.4.15.tar.gz && \
                cd nagios-plugins-1.4.15 && \
                ./configure --with-nagios-user=nagios \
                --with-nagios-group=nagios \
                --with-openssl=/usr/bin/openssl \
                --enable-perl-modules \
                --enable-redhat-pthread-workaround \
                &>/dev/null && \
                make &>/dev/null && \
                make install &>/dev/null
                """)
        # Install openssl-devel
        if self.status['is_openssl_devel'] == 'False':
            print '''Please install those pacages:
                libcom_err-devel-1.41.12-14.el6_4.2.x86_64                                                                                                                    1/6 
                keyutils-libs-devel-1.4-4.el6.x86_64                                                                                                                          2/6 
                libsepol-devel-2.0.41-4.el6.x86_64                                                                                                                            3/6 
                libselinux-devel-2.0.94-5.3.el6_4.1.x86_64                                                                                                                    4/6 
                krb5-devel-1.10.3-10.el6_4.6.x86_64                                                                                                                           5/6 
                openssl-devel-1.0.0-27.el6_4.2.x86_64  '''
            #UUID = None
            #file_name = self.config.get('tools', 'openssl_devel')
            #file = base_dir + "/client/tools/" + file_name
            #UUID = server.download(file, uuid=UUID)
            #self.server.execute("""
                #cd /tmp && \
                #tar zxf nagios-plugins-1.4.15.tar.gz && \
                #cd nagios-plugins-1.4.15 && \
                #./configure --with-nagios-user=nagios \
                #--with-nagios-group=nagios \
                #--with-openssl=/usr/bin/openssl \
                #--enable-perl-modules \
                #--enable-redhat-pthread-workaround \
                #&>/dev/null && \
                #make &>/dev/null && \
                #make install &>/dev/null
                #""")        

        # Install nrpe
        if self.status['is_installed_nrpe'] == 'False' and self.status['is_openssl_devel']=='True':
            UUID1 = None
            UUID2 = None
            file_name1 = self.config.get('tools', 'nrpe')
            file_name2 = self.config.get('tools', 'xinetd_nrpe')
            file1 = base_dir + "/client/tools/" + file_name1
            file2 = base_dir + "/client/" + file_name2
            UUID1 = self.server.download(file1, uuid=UUID1)
            UUID2 = self.server.download(file2, uuid=UUID2)
            self.server.execute("""
                    cd /tmp && 
                    tar zxf nrpe-2.12.tar.gz && 
                    cd nrpe-2.12 && 
                    ./configure  && 
                    make all  && 
                    make install-plugin  && 
                    make install-daemon   && 
                    make install-daemon-config  && 
                    make install-xinetd  &&
                    echo "nrpe     5666/tcp    #nagios nrpe " >> /etc/services && 
                    sed s/NAGIOSIP/%s/g /tmp/nrpe > /etc/xinetd.d/nrpe &&
                    killall nrpe &&
                    /etc/init.d/xinetd restart && 
                    chkconfig --level 345 xinetd on
                    """ % self.ip_monitor)
            
            #cd /tmp && \
            #tar zxf nrpe-2.12.tar.gz && \
            #cd nrpe-2.12 && \
            #./configure  > /dev/null 2>&1 ; \
            #make all > /dev/null 2>&1 && \
            #make install-plugin &>/dev/null && \
            #make install-daemon  &>/dev/null && \
            #make install-daemon-config &>/dev/null && \
            #make install-xinetd  &>/dev/null;
            #sed s/NAGIOSIP/%s/g /tmp/nrpe > /etc/xinetd.d/nrpe;
            #killall nrpe ;
            #/etc/init.d/xinetd restart && \
            #chkconfig --level 345 xinetd on            
            
            
            

        # Install utils_pm
        if self.status['is_installed_utils_pm'] == 'False':
            UUID = None
            file_name = self.config.get('tools', 'utils_pm')
            file = base_dir + "/client/tools/" + file_name           
            UUID = self.server.download(file, uuid=UUID)
            self.server.execute("""
                    mv /tmp/%s /usr/local/nagios/libexec
                    """ % file_name)

    def test_script(self):     
        self.title()
        commands = self.config.items('test_commands')
        command_lines = ""
        for (command, command_line) in commands:
            command_lines += (command_line + ';')
        self.server.execute(command_lines)

    def update_nrpe(self):
        self.title()
        nrpes = self.config.items('nrpe')
        shell = ""
        for name, value in nrpes:
            nrpe_line = "command[" + name + "]=" + value
            shell += """
                    sed -i '/command\[%s/d' \
                    /usr/local/nagios/etc/nrpe.cfg;
                    echo "%s" >> \
                    /usr/local/nagios/etc/nrpe.cfg;
                    """ % (name, nrpe_line)
        self.server.execute(shell)
            
    def review_nrpe(self):
        self.title()
        self.server.execute("""
                egrep -v '^#|^$' \
                /usr/local/nagios/etc/nrpe.cfg \
                | egrep '^command\[.*\]'
                """)
    def update_nrpe_ntp(self):
        self.title()
        ntp=string.strip(self.server.s.ip_ntp_server)
        if len(ntp) > 0:
            self.server.execute("""
                    sed -i 's/NTP_SERVER_IP/%s/g' \
                    /usr/local/nagios/etc/nrpe.cfg
                    """ % ntp)    

    def deploy(self):
        print "check monitor status"
        self.check()
        print "update perl"
        self.upgrade_perl()
        print "install tools"
        self.install_tools()
        print "config iptables"
        self.config_iptables()
        print "deploy monitor script"
        self.deploy_script()
        print "update nrpe"
        self.update_nrpe()
        print "update ntp server in nrpe.cfg"
        self.update_nrpe_ntp()
    def config_centreon(self):
        pass
        

class SysInfo(object):
    # db table class
    __dbclass__=None
    # db session
    __dbsession__=None
    
    __checklist__={}

    #----------------------------------------------------------------------
    @classmethod
    def _get_dbclass(cls):
        if cls.__dbsession__ and cls.__dbclass__:
            return True
        selfclassname=cls.__name__
        dbclassname="t_%s" % string.lower(selfclassname)
        dbclass=None
        dbsession=None        
        import importlib
        mo=importlib.import_module('dbi')
        if mo:
            if hasattr(mo,dbclassname):
                dbclass= getattr(mo,dbclassname)
            if hasattr(mo,'session'):
                dbsession=getattr(mo,'session')
            if dbclass and dbsession:
                cls.__dbsession__=dbsession
                cls.__dbclass__=dbclass
                return True
            else:
                return False
    @classmethod
    def _get_dbinfo(cls,sys_type=None,dbid=None):
        if not cls._get_dbclass():
            return None
        result=None
        
        if sys_type is not None:
            if dbid is not None:
                result=cls.__dbsession__.query(cls.__dbclass__).filter(cls.__dbclass__.sys_type==sys_type and cls.__dbclass__.id==dbid).first()
            else:
                result=cls.__dbsession__.query(cls.__dbclass__).filter(cls.__dbclass__.sys_type==sys_type ).all()
        return result    

    def __init__(self,srv):
        if srv is None:raise "Server Is Null"
        if type(srv) != Server: 
            raise "param type is not Server"
        self.server=srv 
        if len(self.__class__.__checklist__) == 0:
            tlist=self._get_dbinfo(self.server.s.os_type)
            for i in tlist:
                self.__class__.__checklist__[i.id]=i
        self.check_result={}

    def check_item(self,dbid=None,do_update=False):
        check_info=None
        check_return=None
        if self.__class__.__checklist__.has_key(dbid):
            check_info=self.__class__.__checklist__[dbid]
        else:
            return None
        if self.check_result.has_key(dbid):
            check_return=self.check_result[dbid]
            return None
        if not check_info.record_table and check_info.record_field and check_info.check_cmd:
            return None
        if check_info.need_id:
            need_result=self.check_item(check_info.need_id,do_update=False)
            if need_result not in string.split("%s" % check_info.need_value,';'):
                return None
        execute_result=self.server.execute(check_info.check_cmd,hide_puts=True)
        if execute_result.succeed and execute_result.return_code ==0 :
            # reg result
            check_return=string.strip(execute_result.result)
            self.check_result[dbid]=check_return
            if do_update and check_info.record_field and check_info.record_table:
                self.server.s.update_value(check_info.record_field,check_return) 
        return check_return
    def check_all(self,do_update=False):
        for key,value in self.__class__.__checklist__.iteritems():
            print ("Check [%s]=%s" % (value.check_name,self.check_item(value.id,do_update))).encode('gbk')
            
class Transfer(object):
    def __init__(self,server,path):
        
        (self._lpath,self._lfile) = os.path.split(path)
        self.server=server
        self.source_path=None
        self.uuid=str(muuid.uuid1())
        # ServerID: [ Server, status, Result]
        self.trans_list=None
        # ServerID: [ Server, status, Result]
        self.dest_servers=[]
        
        
        self.source_path=path
    def add_server(self,*srvlist):
        for srv in srvlist:
            if type(srv)==Server:
                self.dest_servers.append(srv)
                
    def send(self,dest_path):
        if not self.server.exists(dest_path):
            print "source is not exists"
            return
        if len(self.dest_servers)==0:
            return
        self.trans_list={}
        tmppath=''
        try:
            tmppath=os.environ["TMP"]
        except:
            pass
        if len(tmppath)==0 :tmppath='/tmp'
        #对目标服务器按level进行排序，先传输level数值大的，可以增加
        for value in self.dest_servers if len(self.dest_servers)<2 else self.dest_servers.sort(lambda p1,p2:cmp( 0 if p1 is None else p1.s.level,0 if p2 is None else p2.s.level),reverse=True):
            #记录uuid使用次数，初始是-1.正常结束时0，每传递加1，有问题为-2【记录机器为传输目标机器】
            #记录传输过程的执行结果，文本记录
            walkpath=self.server.walk(self.server,value)
            for (src_srv,dst_srv) in map(None,walkpath,walkpath[1:]):
                if src_srv is not None and not self.trans_list.has_key(src_srv.dbid):
                    self.trans_list[src_srv.dbid]=[src_srv,0,None]
                if dst_srv is not None and not self.trans_list.has_key(dst_srv.dbid):
                    self.trans_list[dst_srv.dbid]=[dst_srv,0,None]                    
                    
                print "%s+-->%s"%(string.ljust(' ',src_srv.level*4,)+str(src_srv),str(dst_srv))
                if src_srv == self.server:
                    if dst_srv.exists(os.path.join(tmppath,self.uuid)):
                        self.trans_list[dst_srv.dbid][1]+=1     
                    else:
                        exe_result=src_srv.execute("scp -r %s %s:%s" % (self.source_path
                                                                        ,"%s@%s" %(dst_srv.s.loginuser,dst_srv.s.ip_oper)
                                                                        ,os.path.join(tmppath,self.uuid)
                                                                        ))
                        if exe_result.succeed:
                            self.trans_list[dst_srv.dbid][1]+=1
                            self.trans_list[dst_srv.dbid][2]='OK'
                        else:
                            self.trans_list[dst_srv.dbid][2]='Not OK' 
                    continue
                if dst_srv == None:
                    print self.trans_list[src_srv.dbid][1]
                    if self.trans_list.has_key(src_srv.dbid) and self.trans_list[src_srv.dbid][1]==1:
                        if src_srv.exists(os.path.join(tmppath,self.uuid)):
                            if not src_srv.exists(dest_path):
                                src_srv.execute("mkdir -p %s" % dest_path)
                            exe_result=src_srv.execute("mv %s %s" % (os.path.join(tmppath,self.uuid)
                                                             ,os.path.join(dest_path,self._lfile)
                                                             ),hide_stdout=False,hide_output_prefix=True,hide_puts=True)
                            if exe_result.succeed:
                                self.trans_list[src_srv.dbid][1]=0
                                print 'send finished'
                            else:
                                print 'send failed:%' % exe_result.result
                        else:
                            print 'No target:%s' % os.path.join(tmppath,self.uuid)
                    break
                if src_srv.level > dst_srv.level and self.trans_list.has_key(src_srv.dbid) and self.trans_list.has_key(dst_srv.dbid):
                    if dst_srv.exists(os.path.join(tmppath,self.uuid)):
                        self.trans_list[dst_srv.dbid][1]+=1
                    else:
                        exe_result=dst_srv.execute("scp -r %s:%s %s" % ("%s@%s" %(src_srv.s.loginuser,src_srv.s.ip_oper)
                                                                        ,os.path.join(tmppath,self.uuid)
                                                                        ,os.path.join(tmppath)
                                                                        ))
                        if exe_result.succeed:
                            self.trans_list[dst_srv.dbid][1]+=1
                            self.trans_list[dst_srv.dbid][2]='OK'
                        else:
                            self.trans_list[dst_srv.dbid][2]='Not OK'
                elif src_srv.level < dst_srv.level and self.trans_list.has_key(src_srv.dbid) and self.trans_list.has_key(dst_srv.dbid):
                    if dst_srv.exists(os.path.join(tmppath,self.uuid)):
                        self.trans_list[dst_srv.dbid][1]+=1   
                    else:
                        exe_result=src_srv.execute("scp -r %s %s:%s" % (os.path.join(tmppath,self.uuid)
                                                                        ,"%s@%s" %(dst_srv.s.loginuser,dst_srv.s.ip_oper)
                                                                        ,os.path.join(tmppath)
                                                                        ))
                        if exe_result.succeed:
                            self.trans_list[dst_srv.dbid][1]+=1
                            self.trans_list[dst_srv.dbid][2]='OK'
                        else:
                            self.trans_list[dst_srv.dbid][2]='Not OK'
                    
                



            
class MySQL(object):
    pass

