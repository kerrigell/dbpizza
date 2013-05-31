# -*- encoding: utf-8 -*-
from fabric.api import puts
from fabric.colors import *

#######################################################################
class Server:
    """"""
    def __init__(self,address,whomai='',user='root',port=22):
        self.address=''
        self.user=user
        self.port=port
        self.whoami=''
        self.level=0
        self.parent=None
        self.childs={}
        self.root=None
    def set_parent(self,par):
        if type(par) != Server:
            return None
        self.parent=par
        if self.address not in par.childs.keys():
            par[self.address]=self
        if not par.root:
            self.root=par
        else:
            self.root=par.root
        self.level=par.level+1
        return self.level
    def search(self,addr):
        def _search(addr,start):
            it=None
            for key in start.childs.keys():
                if key == addr:
                    it=start[key]
                else:
                    it=_search(addr,start.childs[key])
            return it
    def walk(self,addr):
        #seach child
        pass
    def run(self,cmd):
        from fabric.api import run,env,puts
        from fabric.exceptions import NetworkError
        if not self.address:
            return None
        env.host_string='%s@%s:%s' % (self.user,self.address,self.port)
        if gateway:
            env.gateway=self.gateway
        try:
            result=run(cmd,shell=False)
        except NetworkError,e:
            puts('%s Error: #%d %s' % (self.address, e.args[0], e.args[1]))
    def getfile_from(self):
        pass
    def putfile_to(self):
        pass

            
            
        
    
    

@task
def check_service():
    '''kkk '''
    pass

@task
def check_instance():
    '''kkk '''
    pass

@task
def install_service():
    ''' kkk'''
    pass

@task
def create_instance():
    '''kkk '''
    pass

@task
def init_mysqldb():
    '''kkk '''
    pass

@task
def start_instance():
    '''kkk '''
    pass

@task
def stop_instance():
    ''' '''
    pass

@task
def create_database():
    ''' '''
    pass

@task
def init_database():
    ''' '''
    pass

@task
def backup_database():
    ''' '''
    pass

@task
def recovery_database():
    ''' '''
    pass

@task
def changefile(src,des,path):
    execute(
    pass

def _get(src,filep):
    pass

def recover_backup(srcaddr,desaddr,ccaddr):
    with settings(hide('running','stdout'),warn_only=True):
        hstmp=env.host_string
        env.gateway=ccaddr
        result=run('ls -t %s' % backuppath)
        env

