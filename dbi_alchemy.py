#!/usr/bin/env python
#coding:utf-8
# Author:  Haiyang Peng
# Purpose:
# Created: 2013/6/28

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,BigInteger,VARCHAR,Text,DateTime
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.types import SchemaType,TypeDecorator,Enum
from sqlalchemy.orm import mapper,sessionmaker

engine = create_engine('mysql://root@127.0.0.1/dbpizza?charset=latin1')
Base = declarative_base()

class t_server(Base):
    __tablename__ = 't_server'

    id = Column(Interger, primary_key=True)
    pid = Column(Integer)
    region = Column(Enum('hk','vn','id','in','tw','th','us','my','cn'))
    product = Column(Enum('tlbb','ldj','taoyuan','guyu','totem','specialforce','gamefuse','oppaplay','gamiction','cuaban','davinci','swordgirls','zszw','common'))
    role = Column(Enum('cc','backup','db'))
    loginuser = Column(VARCHAR(40))
    description = Column(VARCHAR(250))
    ip_oper = Column(VARCHAR(16))
    ip_private = Column(VARCHAR(16))
    ip_public = Column(VARCHAR(16))
    ip_ilo = Column(VARCHAR(16))
    is_reserve = Column(TINYINT(1))
    dbms = Column(Enum('MySQL','Oracle','MSSQL'))
    vender = Column(Enum('Dell','HP','VMware','Intel','Xen'))
    model = Column(VARCHAR(100))
    os_type = Column(Enum('Linux','Windows'))
    os_release = Column(Enum('RHEL_5_3','RHEL_4_8','RHEL_4_6','CENT_6_3','WIN2003','WIN2008'))
    os_arch = Column(Enum('x86_64','i386'))
