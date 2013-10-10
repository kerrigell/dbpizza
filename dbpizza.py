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
import os.path

import cmd2 as cmd
from cmd2 import options,make_option
import getopt
import pdb

from node import Server
from node import Feature
from node import Monitor

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
        slis=[]
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
            self.pf

    @options([make_option('-P','--piece',type='string',help='piece name')])    
    def do_get(self,arg,opts=None):
        for path in string.split(arg):
            if not os.path.exists(path):
                print self.colorize('Error: Path not exist','red')
            else:
                if opts.piece:
                    if self.piecis.has_key(opts.piece):
                        for value in self.piecis[opts.piece]['servers']:
                            value.download(path)
                    else:
                        print self.colorize('Error: No this piece','red')
                else:
                    self.server.current_node.download(path)
    def complete_get(self,text,line,begidx,endidx):
        import readline
        readline.set_completer_delims(' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>;?')
        import glob
        return glob.glob('%s*' % text)


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
    @options([make_option('-a','--add',action='store_true',help='create piece'),
              make_option('-l','--list',type='string',help='list ipsec'),
              make_option('--source',type='string',help='source address'),
              make_option('--desc',type='string',help='desc address'),
              make_option('--dport',type='string',help='dport'),
              make_option('-r','--rload',action='store_true',help='rload ipsec')
             ])
    def do_ipsec(self,args,opts=None):
        ipsec='''
        IPTABLES=/sbin/iptables;
        $IPTABLES -F;
        $IPTABLES -Z;
        $IPTABLES -X;
        
        $IPTABLES -t mangle -F;
        $IPTABLES -t mangle -Z;
        $IPTABLES -t mangle -X;
        
        $IPTABLES -P INPUT ACCEPT ;  
        
        
        $IPTABLES -I INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT;
        $IPTABLES -I OUTPUT -m state --state NEW,ESTABLISHED,RELATED -j ACCEPT ;
        $IPTABLES -I INPUT -s 127.0.0.1 -j ACCEPT;
        $IPTABLES -P INPUT  ACCEPT;
        
        '''
        #if opts.rload:
            #self.server.current_node.execute(ipsec)

    @options([make_option('-c','--check',action='store_true',help='check monitor deploy status'),
              make_option('-d','--deploy',action='store_true',help='deploy everything automatically'),
              make_option('-s','--step',action='store_true',help='deploy monitor step by step'),
        make_option('-p','--piece',type='string',help='the name of a filter list')])
    def do_monitor(self,args,opts=None):
        serverlist=[]
        if opts.piece:
            if self.piecis.has_key(opts.piece):
                for value in self.piecis[opts.piece]['servers']:
                    serverlist.append(value)
            else:
                print self.colorize('Error: No this piece','red')
        else:
            serverlist.append(self.server.current_node)
        monitorlist=[]
        for s in serverlist:
            monitorlist.append(Monitor(s))
        monopers=[
            ['check current status',                                     'check'          ],
            ['upgrade perl from v5.8.5 to v5.8.9',                       'upgrade_perl'   ],
            ['instal nrpe and nagios plug-in',                           'install_tools'  ],
            ['deploy all monitor scripts',                               'deploy_script'  ],
            ['open ping and 5666 for nagios monitor servers',            'config_iptables'],
            ['update your nrpe commands',                                'update_nrpe'    ],
            ['review all your commands currently defined in nrpe.cfg',   'review_nrpe'    ],
            ['test monitor script',                                      'test_script'    ]
            ]
        oper=None
        if opts.step:
            sauce = self.select([x[0] for x in monopers],'Please choice what you want?')
            dopers=dict(monopers)
            if dopers.has_key(sauce):
                oper=dopers[sauce]
        elif opts.check:
            oper='check'
        elif opts.deploy:
            oper='deploy'
        for item in monitorlist:
            if oper:
                operfun=getattr(item,oper)
                operfun()


    def complete_ipsec(self,text,line,begidx,endidx):
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

#def import_file(modulename):
    #dirname = os.path.dirname(os.path.abspath(modulename))
    #filename, ext = os.path.splitext(os.path.basename(modulename))
    #if ext.lower() != '.py':
        #return {}, {}
    #if sys.modules.has_key(filename):
        #del sys.modules[filename]
    #if dirname:
        #sys.path.insert(0, dirname)
    #mod = __import__(filename)
    #if dirname:
        #del sys.path[0]
    #return mod

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
