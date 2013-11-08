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
from node import Nagios
from node import IPsec
from node import SysInfo
from node import Transfer
from node import Security

import paramiko
class PizzaShell(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
      
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
    #def do_put(self,line):
        #'''put a file to target server from ccs'''
        #(lfile, taddr, rpath)=string.split(line)
        #if not (os.path.isfile(lfile) and os.path.exists(lfile)):
            #print 'Error: not exists or not a file %s' % lfile
            #return
        #tsrv=self.root.search(taddr)
        #if tsrv == None:
            #print 'Error: not find %s' % taddr
            #return
        #print 'Send a file from %s to %s' % (self.root, tsrv)
        #self.root.putfile(lfile,tsrv,rpath)
        #print 'Send finished'

    #def help_put(self):
        #print '\n'.join(['put <localfile> <targetserver> <remotepath>','put a file to target server from ccs'])

    #def complete_put(self,text,line,begidx,endidx):
        #import readline
        #pos=len(string.split(line))
        #if pos == 2 or pos == 4:
            ## import rlcompleter
            ## readline.parse_and_bind("tab: complete")   
            #readline.set_completer_delims(' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>;?')
            #import glob
            #return glob.glob('%s*' % text)
        #if pos == 3:
            #'''search server list like aaa.*'''
            #readline.set_completer_delims(' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>;?')
            #return self.root.search_list(text)

    def do_cmd(self,args):
        self.stdout.write(args.parsed.dump()+'\n')
        #for s in self._get_operation_list(opts):
            #s.execute(arg)
        

    #@options([make_option('-p','--piece',type='string',help='piece name'),
              #make_option('--desc_path',type='string',help='piece name')])    
    #def do_get(self,arg,opts=None):
        #for path in string.split(arg):
            #if not os.path.exists(path):
                #print self.colorize('Error: Path not exist','red')
                #continue
            #else:
                #for s in self._get_operation_list(opts):
                    #s.download(path,targetpath=opts.desc_path if opts.desc_path else None)
    #def complete_get(self,text,line,begidx,endidx):
        #import readline
        #readline.set_completer_delims(' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>;?')
        #import glob
        #return glob.glob('%s*' % text)


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
    def _get_operation_list(self,opts):
        serverlist=[]
        if opts is not None and hasattr(opts,'piece') and self.piecis.has_key(opts.piece):
            for value in self.piecis[opts.piece]['servers']:
                serverlist.append(value)
        else:
            serverlist.append(self.server.current_node)  
        return serverlist


    @options([make_option('-c','--check',action='store_true',help='check monitor deploy status'),
              make_option('-d','--deploy',action='store_true',help='deploy everything automatically'),
              make_option('-s','--step',action='store_true',help='deploy monitor step by step'),
        make_option('-p','--piece',type='string',help='the name of a filter list')])
    def do_nagios(self,args,opts=None):
        monitorlist=[]
        for s in self._get_operation_list(opts):
            monitorlist.append(Nagios(s))
        monopers=[
            ['check current status',                                     'check'          ],
            ['upgrade perl from v5.8.5 to v5.8.9',                       'upgrade_perl'   ],
            ['instal nrpe and nagios plug-in',                           'install_tools'  ],
            ['deploy all monitor scripts',                               'deploy_script'  ],
            ['open ping and 5666 for nagios monitor servers',            'config_iptables'],
            ['update your nrpe commands',                                'update_nrpe'    ],
            ['update ntp server address in your nrpe.cfg',               'update_nrpe_ntp'],
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
    @options([make_option('-a','--add',action='store_true',help='add ipsec filter'),
              make_option('--chain',type='choice',choices=['INPUT','OUTPUT','FORWARD'],help='protocal'),
              make_option('--source',type='string',help='source address'),
              make_option('--protocal',type='choice',choices=['tcp','udp','imcp','all'],help='protocal'),
              make_option('--dport',type='string',help='dport'),
          #    make_option('--description',type='string',help='filter description'),              
              make_option('-d','--delete',action='store_true',help='delete ipsec filter'),
              make_option('-l','--list',action='store_true',help='list ipsec'),
              make_option('--script',action='store_true',help='show  ipsec script'),
              make_option('--status',action='store_true',help='show  current ipsec status'),
              make_option('--reload',action='store_true',help='reload ipsec')
             ])
    def do_ipsec(self,args,opts=None):
        cipsec=IPsec(self.server.current_node)
        if opts.add:
            if opts.protocal and opts.source and opts.dport :
                cipsec.add_filter(opts.protocal,opts.source,opts.dport,args,chain= opts.chain if opts.chain else 'INPUT')
            else:
                print '''Need surport correct value for those:
        [--chain=]
        --source=
        --protocal=
        --dport=
        --description='''
            return
        if opts.list:
            ripsec=cipsec.list()
            print "%5s%8s%20s%20s  %s" % ("dbid","Chain",'Source','dport','description')
            for i in ripsec:
                print "%5s%8s%20s%20s  %s" % (i.id,i.chain,i.source_addr,i.dport,i.description)
            return
        if opts.script:
            print cipsec.make_script()
            return
        if opts.reload:
            print 'start reload ipsec',
            cipsec.reload()
            print 'ok'
            return
        if opts.delete:
            ripsec=cipsec.list()
            print "      %5s%8s%20s%20s  %s" % ("dbid","Chain",'Source','dport','description')
            infolist=[]
            for i in ripsec:
                infolist.append("%5s%8s%20s%20s  %s" % (i.id,i.chain,i.source_addr,i.dport,i.description))
            sauce=self.select(infolist)
            print "delete filter",
            cipsec.del_filter(int(string.split(sauce)[0]))
            print "ok"
            return
        if opts.status:
            self.server.current_node.execute("iptables -nvL")
            return
    @options([make_option('--check_all',action='store_true',help='check all'),
              make_option('--update',action='store_true',help='update database'),
              make_option('-p','--piece',type='string',help='piece name')])        
    def do_info(self,arg,opts=None):
        infolist=[]
        for s in self._get_operation_list(opts):
            infolist.append(SysInfo(s))
        for i in infolist:
            print i.server
            if opts.check_all:
                i.check_all(do_update= True if opts.update else False)
    @options([make_option('-p','--piece',type='string',help='piece name'),
              make_option('-t','--target',type='string',help='trans target'),
              make_option('-d','--deploy_dir',type='string',help='trans target'),
              make_option('-w','--who',type='string',help='trans target')])  
    def do_trans(self,arg,opts=None):
        trans_task=Transfer(self.server.current_node,opts.target)
        if opts.who:
            line=string.strip(opts.who)
            dbid=line
            if string.find(line,'[') !=-1:
                (dbid,info)=string.split(line,'[')
                (dbid,info)=string.split(info,':')   
                trans_task.add_server(self.server.current_node.get_node(int(dbid)))
        if opts.piece:
            for s in self._get_operation_list(opts):
                trans_task.add_server(s)
        trans_task.send( opts.deploy_dir if opts.deploy_dir else '/tmp')
        trans_task.clear()

    @options([make_option('-p','--piece',type='string',help='piece name'),
              make_option('-a','--make_authorized',action='store_true',help='piece name')])  
    def do_security(self,arg,opts=None):
        import getpass
        infolist=[]
        for s in self._get_operation_list(opts):
            infolist.append(Security(s))
        password=None
        for i in infolist:        
            if opts.make_authorized:
                if password is None:
                    password = getpass.getpass('Enter Login password: ')
                i.make_authorized(password=password if len(password)> 0 else None)
    @options([make_option('-p','--piece',type='string',help='piece name'),
              make_option('-d','--deploy',action='store_true',help='piece name'),
              make_option('-s','--start',action='store_true',help='piece name'),
              make_option('-t','--stop',action='store_true',help='piece name')])     
    def do_axis(self,arg,opts=None):
        from node import Axis
        infolist=[]
        for s in self._get_operation_list(opts):
            infolist.append(Axis(s))
        for i in infolist:        
            if opts.deploy:
                i.deploy()
            if opts.start:
                i.start()
            if opts.stop:
                i.stop()

                    
        
            

 
 
 
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
