#!/usr/bin/env python
#coding:utf-8
# Author:  Jianpo Ma
# Purpose:
# Created: 2013/3/29

import os,sys
import string
import unittest
import traceback
#import cmd
import subprocess
import time

import cmd2 as cmd
from cmd2 import options,make_option
import getopt
import pdb

from node import Server
from node import Feature

import paramiko
class PizzaShell(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.rootNode=Server()
        self.currentNode=self.rootNode
        self.rootNode.breed()
        
        #using
        self.server=Server()
        self.server.breed()
        self.feature=Feature(foreignclass=Server)
        self.feature.breed(True)
        self.piecis={}
        self.mode=Server
        self.prompt="Pizza [%s]>" % self.mode.current_node

    def do_pwd(self,line):
        print self.mode.current_node

    def do_cd(self,line):
        line=string.strip(line)
        dbid=line
        if string.find(line,'[') !=-1:
            (dbid,info)=string.split(line,'[')
            (dbid,info)=string.split(info,':')
        cnode=self.mode.cd(dbid)
        self.prompt="Pizza [%s]>" % cnode

    def complete_cd(self,text,line,begidx,endidx):
        import readline
        readline.set_completer_delims(' \t\n`~!@#$%^&*()-=+[{]}\\|;\'",<>;?')
        tlist=[str(i) for i in self.mode.current_node.childs.values() if string.find(str(i),line[3:]) ==0]
        return tlist
    def do_login(self,line):
        if self.mode==Server:
            self.mode.current_node.login()
    def do_mode(self,line):
        line=string.strip(line)
        if line == 'product':
            self.mode=Feature
        elif line == 'server':
            self.mode=Server
        self.prompt="Pizza [%s]>" % self.mode.current_node
    def complete_mode(self,text,line,begidx,endidx):
        modelist=['product','server']
        return [ f for f in modelist if f.startswith(text)]
    def do_put(self,line):
        '''put a file to target server from ccs'''
        (lfile, taddr, rpath)=string.split(line)
        if not (os.path.isfile(lfile) and os.path.exists(lfile)):
            print 'Error: not exists or not a file %s' % lfile
            return
        tsrv=self.root.search(taddr)
        if tsrv == None:
            print 'Error: not find %s' % taddr
            return
        print 'Send a file from %s to %s' % (self.root, tsrv)
        self.root.putfile(lfile,tsrv,rpath)
        print 'Send finished'

    def help_put(self):
        print '\n'.join(['put <localfile> <targetserver> <remotepath>','put a file to target server from ccs'])

    def complete_put(self,text,line,begidx,endidx):
        import readline
        pos=len(string.split(line))
        if pos == 2 or pos == 4:
            # import rlcompleter
            # readline.parse_and_bind("tab: complete")   
            readline.set_completer_delims(' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>;?')
            import glob
            return glob.glob('%s*' % text)
        if pos == 3:
            '''search server list like aaa.*'''
            readline.set_completer_delims(' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>;?')
            return self.root.search_list(text)
    @options([make_option('-P','--Piece',type='string',help='piece name'),
              make_option('-c','--command',type='string',help='command')])
    def do_cmd(self,arg,opts=None):
        if opts.Piece and opts.command:
            if self.piecis.has_key(opts.Piece):
                for s in self.piecis[opts.Piece]['servers']:
                    result=s.execute(opts.command)
            else:
                print self.colorize('piece name not exist','red')
                return
        elif opts.command:
            self.server.current_node.execute(opts.command)


    def do_get(self,line):
        opts,args = getopt.getopt(string.split(line),'iR',)
        path=' '.join(args)
        infect=False
        extent=False
        for opt,arg in opts:
            if opt in ('-i'):
                infect=True
            elif opt in ('-R'):
                extent=True
        uuid=self.currentNode.download(path)
        if infect:
            self.currentNode.infect_download(path=path,extent=extent,uuid=uuid)




    @options([make_option('-p','--path',type='string',help='source path')])    
    def do_put(self,arg,opts=None):
        if opts.path:
            import os.path
            if os.path.exists(opts.path):
                self.server.current_node.download(opts.path)
            else:
                print self.colorize('Error: Path not exist','red')
        

    def do_instance(self,line):
        pass

    def do_use(self,line):
        pass

    #def do_shell(self,line):
        #sub_cmd=subprocess.Popen(line,
                                 #shell=True,
                                 #stdout=subprocess.PIPE)
        #output=sub_cmd.communicate()[0]
        #print output

    def do_node(self,line):
        import dbapi
        tt=dbapi.servers()
        print 'skdf'
    @options([make_option('-c','--create',action='store_true',help='create piece'),
              make_option('-p','--ploy',type='string',help='the ploy for choice servers'),
              make_option('-l','--list',action='store_true',help='list piece'),
              make_option('-d','--delete',action='store_true',help='delete piece'),
              make_option('-n','--name',type='string',help='piece name')])
    def do_piece(self,arg,opts=None):
     #   parser=argparse.
        arg=''.join(arg)
        if opts.create and opts.name and opts.ploy:
            piece={'ploy':opts.ploy,
                   'createtime':time.ctime(),
                   'servers':[]}
            if self.mode == Server:
                slist=self.mode.piece(opts.ploy)
                piece['servers']=slist
                self.piecis[opts.name]=piece
                if slist:
                    for i in slist:
                        print i
        elif opts.list:
            for i in self.piecis.keys():
                print i
                if opts.name:
                    print ' '.ljust(4,' '),'CreateTime:',self.piecis[i]['createtime']
                    for j in self.piecis[i]['servers']:
                        print ' '.ljust(4,' '),j
        elif opts.run:
            pass
    @options([make_option('-c','--create',action='store_true',help='create piece'),
              make_option('-p','--ploy',type='string',help='the ploy for choice servers'),
              make_option('-l','--list',action='store_true',help='list piece'),
              make_option('-d','--delete',action='store_true',help='delete piece'),
              make_option('-n','--name',type='string',help='piece name')])
    def do_ipsec(self,text,line,begidx,endidx):
        import shlex
        tlist=shlex.shlex(line)
        tlen=len(tlist)
        print tlist
    def complete_ipsec():
        pass

class Logger(object):
    def __init__(self, filename="Default.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "a")
        self.mode='ip or product'
        self.current='target'

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.terminal.close()
        self.log.close()

    def isatty(self):
        return False

def import_file(modulename):
    dirname = os.path.dirname(os.path.abspath(modulename))
    filename, ext = os.path.splitext(os.path.basename(modulename))
    if ext.lower() != '.py':
        return {}, {}
    if sys.modules.has_key(filename):
        del sys.modules[filename]
    if dirname:
        sys.path.insert(0, dirname)
    mod = __import__(filename)
    if dirname:
        del sys.path[0]
    return mod

def main():
    #log_file=r"dbpizza.log"
    #sys.stdout = Logger(log_file)
    #sys.stderr = sys.stdout
    if len(sys.argv)>1:
        PizzaShell().onecmd(' '.join(sys.argv[1:]))
    else:
        PizzaShell().cmdloop()



if __name__=='__main__':  
    main()
