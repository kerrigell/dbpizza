#!/usr/bin/env python
#coding:utf-8
# Author:  Haiyang Peng
# Purpose:
# Created: 2013/6/28

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,BigInteger,VARCHAR,Text,DateTime,DATETIME
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.types import SchemaType,TypeDecorator,Enum
from sqlalchemy.orm import sessionmaker

import time,datetime
engine = create_engine('mysql://root@dbpizzzahost/dbpizza?charset=utf8')
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class t_server(Base):
    __tablename__ = 't_server'
    __searchword__ = None
    id = Column(Integer, primary_key=True)
    pid = Column(Integer)
    region = Column(Enum('hk','vn','id','in','tw','th','us','my','cn'))
    product = Column(Enum('tlbb','ldj','taoyuan','guyu','totem','specialforce','gamefuse','oppaplay','gamiction','cuaban','davinci','swordgirls','zszw','common','pengyou'))
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
    ip_monitor=Column(VARCHAR(16))
    ip_ntp_server=Column(VARCHAR(16))
    serial=Column(VARCHAR(50))
    def __repr__(self):
        return "<Server('%s','%s','%s')>" % (self.region, self.product, self.ip_oper)
    @classmethod
    def _all_words(cls):
        if cls.__searchword__:
            return cls.__searchword__
        words = []
        words += cls._get_word(t_server.region)
        words += cls._get_word(t_server.product)
        words += cls._get_word(t_server.role)
        words += cls._get_word(t_server.dbms)
        words += cls._get_word(t_server.vender)
        words += cls._get_word(t_server.os_type)
        words += cls._get_word(t_server.os_release)
        words += cls._get_word(t_server.os_arch)
        words += [('reserve',t_server.is_reserve)]
        words = dict(words)
        cls.__searchword__=words
        return cls.__searchword__
    @classmethod
    def _get_word(cls,col):
        ret = session.query(col).filter(col != None).distinct().all()
        return [ (str(x[0]),col) for x in ret ]    
    @classmethod
    def piece(cls,keywords):
        import string
        keywords=string.split(keywords,',')
        words = cls._all_words()
        knife = {}
        for i in keywords:
            if i in words.keys():
                knife[i] = words[i]
        if len(knife.keys())<=0:
            return []
        result=session.query(t_server)
        for value, col in knife.iteritems():
            result = result.filter(col == value)
        result = result.all()
        return [ i.id for i in result]

class t_feature(Base):
    __tablename__ = 't_feature'
    id = Column(Integer, primary_key=True)
    pid = Column(Integer)
    feature = Column(VARCHAR(50))
    detail = Column(VARCHAR(50))
    server_id = Column(Integer)
    fabric = Column(VARCHAR(50))
    exec_info=Column(VARCHAR(200))
    
class t_ipsec(Base):
    __tablename__='t_ipsec'
    id = Column(Integer, primary_key=True)
    server_id = Column(Integer)
    chain = Column(Enum('INPUT','OUTPUT','FORWARD'))
    source_addr = Column(VARCHAR(50))
    dest_addr = Column(VARCHAR(50))
    protocal = Column(Enum('tcp','udp','icmp','all'))
    dport = Column(VARCHAR(50))
    #
    status = Column(Integer) 
    description = Column(VARCHAR(100))
    createdate=Column(DATETIME)
    modifydate=Column(DATETIME)
    def __init__(self,server_id,protocal,source_addr,dport,description,status=0,chain='INPUT'):
        self.chain=chain
        self.server_id=server_id
        self.chain=chain
        self.source_addr=source_addr
        self.protocal=protocal
        self.dport=dport
        self.status=status
        self.description=description
        #self.createdate=time.localtime(time.time())
        #self.modifydate=self.createdate