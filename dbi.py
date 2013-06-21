#!/usr/bin/env python
#coding:utf-8
# Author:  Jianpo Ma 
# Purpose: 
# Created: 2013/6/17

import sys
import sqlobject
from sqlobject.mysql import builder

conn=builder()(user='root', password='',host='127.0.0.1',db='dbpizza')

class t_server(sqlobject.SQLObject):
    class sqlmeta:
        table='t_server'
    _connection=conn
    pid=sqlobject.IntCol('pid',length=11,default=None)
    region=sqlobject.EnumCol(enumValues=['hk','vn','id','tw','th','us','my','cn','in',None],default=None)
    product=sqlobject.EnumCol(enumValues=['tlbb','ldj','taoyuan','guyu','totem','specialforce','gamefuse','oppaplay','gamiction','cuaban','davinci','swordgirls','common','zszw'],default=None)
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
