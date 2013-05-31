#!/usr/bin/env python
#coding:utf-8
# Author:  Jianpo Ma
# Purpose: 
# Created: 2013/3/29
from fabric.api import env,run,get,put,local,settings,cd,hide,execute,puts,task,cd,lcd,prefix,local
from fabric.colors import *
import subprocess

import os
import glob
import datetime
import sys
import string

env.roledefs = {
    'tw_ty_gamedb':['administrator@192.168.78.56','administrator@192.168.78.59','administrator@192.168.78.62'],
    'tw_ty_gmtooldb':['administrator@192.168.78.52'],
    'tw_ty_realmportdb':['administrator@192.168.78.53'],
    'tw_ty_databackup':['root@192.168.78.51'],
    'tw_ty_reserve':['administrator@192.168.78.64'],
    'tw_ty_test':['administrator@210.66.186.113'],
    'tw_ty_cc':['root@113.196.124.12']
    }
env.gateway='root@113.196.124.12'

def print_result(result,hopevalue=None,prefix=None):
    code=-99
    try:
        code=result.return_code
    except:
        pass
    if result.succeeded:
        if len(result):
            puts(yellow("ReturnCode:%s" % result.return_code if code <> -99 else '') 
                        + green('\n' + result)
                        ,show_prefix=prefix)
            if hopevalue and result != hopevalue:
                puts(red("The Result is not hope"),show_prefix=prefix)
                return 0
            return 1
    if result.failed:
        #result.return_code == 1
        puts(yellow("ReturnCode:%s" % result.return_code if code <> -99 else '') 
                + red('\n' + result)
                ,show_prefix=prefix)    
        return 0


@task
def ROLEINFO():
    '''rolelist:tw_ty_gamedb,tw_ty_gmtooldb,tw_ty_realmportdb,tw_ty_databackup,tw_ty_reserve,tw_ty_test,tw_ty_cc'''
    return
@task
def updatedb(lsql,database='',getlog=False):
    '''updatedb:lsql=<sqlfile>,database=<databasename>[,getlog=False]'''
    if os.path.isdir(lsql) or not os.path.exists(lsql):
        print 'Error: The path is not exist -> %s' % lsql
        return
    (lsqlpath,lsqlfile)=os.path.split(lsql)
    strnow=datetime.datetime.now().strftime('%Y%m%d%H%M')
    updatedir="%s_%s" % (strnow,database)
    logfile="%s_update_%s_%s.log" % (env.host_string,updatedir,lsqlfile)
    remotepath="/home/dba/version/%s/" % ( updatedir)
    remotesql="%s%s" % (remotepath,lsqlfile) 
    remotelog="/home/dba/logs/%s" % (logfile)
    remotewsql=r'c:\dba\version\%s\%s' % (updatedir,lsqlfile)
    remotewlog=r'c:\dba\logs\%s' % (logfile)
    with settings(hide('stdout'),warn_only=True):
        result=run("mkdir -p %s" % remotepath,shell=False)
        if result.failed:
            puts(red("returncode:%s" % result.return_code))
            puts(red("\n" + result))
            return
        result=put(lsql,remotesql,mode=0750)
        if result.failed:
            puts(red("returncode:%s" % result.return_code))
            puts(red("\n" + result))
            return
    if len(database):
        scmd="sqlcmd -E -d %s -i '%s' -o '%s'" % ( database,remotewsql,remotewlog)
    else:
        scmd="sqlcmd -E  -i '%s' -o '%s'" % ( remotewsql,remotewlog)
    with settings(hide('stdout'),warn_only=True):
        result=run(scmd,shell=False)
        if result.failed:
            puts(red("returncode:%s" % result.return_code))
            puts(red('\n' + result))
            return
        if result.succeeded:
            puts(green('\n' + run("cat %s" % remotelog,shell=False)))
            if getlog:
                get(remotelog,'/home/dba/logs/')
        puts(cyan("update finished"))
    #sqllist=glob.glob(os.path.join(os.path.realpath(path) + '*.sql'))
    #glob.ig
    #for f in flist:
        #pass
@task
def checkconnect(user):
    '''checkconnect:user=<loginuser>'''
    scmd="sqlcmd -E -W -s\";\" -Q \"exec sp_who @loginame='%s'\"" % user
    with settings(hide('stdout'),warn_only=True):
        result=run(scmd, shell=False)
        print_result(result)
@task            
def putfiles(local,remotedir):
    '''putfiles:local=<localdir>,remotedir=<>remotedir>'''
    with settings(hide('stdout'),warn_only=True):
        result=put(local,remotedir,mode=0750)
        print_result(result)
@task        
def execute(cmd,useshell=False):
    '''execute:cmd=<cmd>'''
    with settings(hide('stdout'),warn_only=True):
        result=run(cmd, shell=useshell)
        print_result(result)
@task
def backup(database,backuptype='full',prefix=''):
    '''backup:database=<databasename>[,backuptype=<full,differential,log>[,prefix=<backupfileprefix>]]'''
    bakfile="%smssql_bakup_%s_%s_%s.bak.zip" % ( prefix + ('_' if len(prefix)>0 else ''),
                                                database,
                                                datetime.datetime.now().strftime('%Y%m%d_%H%M'),
                                                backuptype)
    cmd="msbp backup db\(database=%s\;backuptype=%s\;checksum\) local\(path=\'e:\\ms_backup\\%s\'\)" % (database,backuptype,bakfile)
    with settings(hide('stdout'),warn_only=True):
        result=run(cmd, shell=False)
        if print_result(result):
            cmd='cd /home/databackup/;md5sum %s > %s.md5;cat %s.md5' % (bakfile,bakfile,bakfile)
            result=run(cmd,shell=False)
            print_result(result)
@task        
def installcygwin(localfile,target,password=r'e04su3su;6',username='administrator'):
    '''installcygwin:local=<>,target=<>,password=<>[,username=<administrator>]'''
    if not os.path.isfile(localfile):
        puts(red('Error: Not a file(%s)' % local))
        return
    (fpath,fname)=os.path.split(localfile)
    with settings(hide('stdout'),warn_only=True):
        with lcd(fpath):
            lmd5=local("md5sum %s" % fname,capture=True)
            #print_result(lmd5)
        with prefix('mkdir -p /home/dba/packages/'):
            with cd('/home/dba/packages/'):
                rmd5=run("md5sum %s" % fname,shell=False)
                #print_result(rmd5)
                puts(blue("Compare the file's md5"))
                if lmd5 <> rmd5:
                    puts(red("Error: MD5 is different."))
                    puts(blue("Put %s to %s:/home/dba/packages/" % (localfile,env.host)))
                    put(localfile,'/home/dba/packages/',mode=0750)
                    rmd5=run("md5sum %s" % fname,shell=False)
                    if rmd5 <> lmd5:
                        puts(yellow("Error: File MD5 Failue"))
                        return
                smbcmd="smbclient //%s/c$ -U %s%%%s -c \"lcd /home/dba/packages;put %s;quit\"" % (target,username,password,fname)
                with settings(hide('stdout','running'),warn_only=True):
                    puts(blue("Send file with smbclient: %s\\\\\c:\\%s" % (target,fname)))
                    if print_result(run(smbcmd,shell=False)):
                        puts(yellow("Send File Successed"))
                        puts(blue("Please Login this server to install."))
                    else:
                        puts(red("Send File Failure"))
                    
