#!/usr/bin/env python
#coding:utf-8
# Author:  Jianpo Ma
# Purpose: 
# Created: 2013/3/29

import os,sys
import string
import unittest
import traceback
import cmd
import subprocess

from server import Server,servers
import sqlobject
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

class PizzaShell(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt="Pizza>"
        self.root=None
        self._init_servers(0,self.root)
        self.current=self.root
    def _kdf(self):
        welcome='''DB Pizza '''
    def _init_servers(self,pid,parent):
        result=list(servers.select(servers.q.pid==pid))
        if len(result) != 1 and pid ==0:
            return
        for i in result:
            tsrv=Server(i,parent)
            if pid==0:
                self.root=tsrv
            self._init_servers(i.id,tsrv)

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
    def do_cmd(self,line):
        li =string.split(line,'"')
        taddr=string.strip(li[0])
        tcmd=''.join(li[1:])
        tsrv=self.root.search(taddr)
        if tsrv == None:
            print 'Error: not find %s' % taddr
            return
        print tsrv.run(tcmd)
    def do_exit(self,line):
        print '%s: %s' % ('bye',line)
        exit()
    def do_EOF(self,line):
        return True
    def do_cd(self,line):
        print 'aa'
    def complete_cd(self,text,line,begidx,endidx):
        
        tlist=[i.s.ip_oper for i in self.current.childs.values()]
        return tlist
    def do_shell(self,line):
        sub_cmd=subprocess.Popen(line,
                                 shell=True,
                                 stdout=subprocess.PIPE)
        output=sub_cmd.communicate()[0]
        print output
    def do_addserver(self,line):
        import dbapi
        tt=dbapi.servers()
        print 'skdf'
        
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