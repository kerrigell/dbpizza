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
    def execute(self,cmd,hide_running=True,hide_stdout=True,hide_stderr=False,hide_output_prefix=False,hide_puts=False):
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
                if hide_puts is True:
                    return run(cmd,shell=False)
                else:
                    return Server._print_result(run(cmd,shell=False),showprefix=False,info=str(self))
        except NetworkError,e:
          #  traceback.print_exc()
           # print '%s Error: #%d %s' % (target.address, e.args[0], e.args[1])
          #  return ''
            puts(red("Error: %s \n #%s" % (host_string,e)))
            return 0
        except Exception,e:
          #  traceback.print_exc()
            puts(red("Error: %s \n #%s" % (host_string,e)))
         #   print '%s Error: #%d %s' % (target.address, e.args[0], e.args[1])
            return 0
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
            filename = [ x for x in path.split('/') if x ][-1] 
            parent = self.parent
            local_ip = self.s.ip_oper
            local_user=self.s.loginuser
            if uuid == -1:
                return -1
            elif uuid is not None:
                if parent.exists("/tmp/%s" % uuid):
                    if parent.execute("scp -r /tmp/%s %s@%s:/tmp/%s" % (uuid,local_user,local_ip,uuid),hide_stdout=False,hide_output_prefix=True,hide_puts=True):
                        puts(yellow("%s+-->%s"%(string.ljust(' ',self.level*4,),str(self))),show_prefix=False)
                        self.execute("cp -r /tmp/%s /tmp/%s" %(uuid, filename),hide_stdout=False,hide_output_prefix=True,hide_puts=True)
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
                        if parent.execute("scp -r /tmp/%s %s@%s:/tmp/%s" % (uuid,local_user,local_ip,uuid),hide_stdout=False,hide_output_prefix=True,hide_puts=True):
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
                    

class IPsec(object):
    pass
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
            """ % (script_shell, self.ip_monitor, self.ip_monitor, self.ip_monitor)
        raw_status=self.server.execute(shell,hide_puts=True)
        self.status = dict([ x.split()[0].split(':') for x in raw_status.split('\n') if x ])
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
            if self.status['is_installed_%s' % script] == 'False':
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
        UUID = None
        file_name = self.config.get('tools', 'Linux_pm')
        file = base_dir + "/client/tools/" + file_name

        if self.status['is_installed_Linux_pm'] == 'False':
            UUID = self.server.download(file, uuid=UUID)
        if self.status['is_installed_Linux_pm'] == 'False':
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
        UUID = None
        file_name = self.config.get('tools', 'nagios_plugin')
        file = base_dir + "/client/tools/" + file_name
        if self.status['is_installed_nagios_plugin'] == 'False':
            UUID = server.download(file, uuid=UUID)
        if self.status['is_installed_nagios_plugin'] == 'False':
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

        # Install nrpe
        UUID = None
        UUID2 = None
        file_name = self.config.get('tools', 'nrpe')
        file_name2 = self.config.get('tools', 'xinetd_nrpe')
        file = base_dir + "/client/tools/" + file_name
        file2 = base_dir + "/client/" + file_name2
        if self.status['is_installed_nrpe'] == 'False':
            UUID = self.server.download(file, uuid=UUID)
            UUID2 = self.server.download(file, uuid=UUID2)
        if self.status['is_installed_nrpe'] == 'False':
            self.server.execute("""
                    cd /tmp && \
                    tar zxf nrpe-2.12.tar.gz && \
                    cd nrpe-2.12 && \
                    ./configure  > /dev/null 2>&1 ; \
                    make all > /dev/null 2>&1 && \
                    make install-plugin &>/dev/null && \
                    make install-daemon  &>/dev/null && \
                    make install-daemon-config &>/dev/null && \
                    make install-xinetd  &>/dev/null;
                    sed s/NAGIOSIP/%s/g /tmp/nrpe > /etc/xinetd.d/nrpe:
                    killall nrpe ;
                    /etc/init.d/xinetd restart && \
                    chkconfig --level 345 xinetd on
                    """ % self.ip_monitor)

        # Install utils_pm
        UUID = None
        file_name = self.config.get('tools', 'utils_pm')
        file = base_dir + "/client/tools/" + file_name
        if self.status['is_installed_utils_pm'] == 'False':
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
        print self.server.execute(command_lines,hide_puts=True)

    def update_nrpe(self):
        self.title()
        nrpes = self.config.items('nrpe')
        shell = ""
        for name, value in nrpes:
            nrpe_line = "command[" + name + "]=" + value
            shell += """
                    sed -i '/command[%s/d' \
                    /usr/local/nagios/etc/nrpe.cfg;
                    echo "%s" >> \
                    /usr/local/nagios/etc/nrpe.cfg;
                    """ % (name, nrpe_line)
        self.server.execute(shell,hide_puts=True)
            
    def review_nrpe(self):
        self.title()
        print self.server.execute("""
                egrep -v '^#|^$' \
                /usr/local/nagios/etc/nrpe.cfg \
                | egrep '^command\[.*\]'
                """,hide_puts=True)

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
    def config_centreon(self):
        pass
        
        