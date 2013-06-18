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

from node import Server


class PizzaShell(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        
        self.rootNode=Server()
        self.currentNode=self.rootNode
        self.rootNode.breed()
        self.prompt="Pizza [%s]>" % self.currentNode
    def do_pwd(self,line):
        print self.currentNode


    def do_cd(self,line):
        line=string.strip(line)
        if line == '..':
            if self.currentNode <> self.rootNode:
                self.currentNode=self.currentNode.parent
                self.prompt="Pizza [%s]>" % self.currentNode
                return
        elif line == '':
            return
        
        (dbid,info)=string.split(line,'[')
        (dbid,info)=string.split(info,':')
        
        if self.currentNode.childs.has_key(int(dbid)):
            self.currentNode=self.currentNode.childs[int(dbid)]
            self.prompt="Pizza [%s]>" % self.currentNode
            if self.currentNode.childs is None:
                self.currentNode.breed()

    def complete_cd(self,text,line,begidx,endidx):
        print "text:%s" % text
        print "line:%s" % line
        tlist=[str(i) for i in self.currentNode.childs.values() if string.find(str(i),text) ==0]
        print tlist
        return tlist
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
        print line
        self.currentNode.run(line)

    def do_exit(self,line):
        print '%s: %s' % ('bye',line)
        exit()
    def do_EOF(self,line):
        return True

    def do_ls(self,line):
        pass
    def do_put(self,line):
        pass
    def do_get(self,line):
        pass
    def do_set(self,line):
        pass
    def do_instance(self,line):
        pass
    def do_use(self,line):
        pass
    def do_shell(self,line):
        sub_cmd=subprocess.Popen(line,
                                 shell=True,
                                 stdout=subprocess.PIPE)
        output=sub_cmd.communicate()[0]
        print output
    def do_node(self,line):
        import dbapi
        tt=dbapi.servers()
        print 'skdf'
    def do_piece(self,line):
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
