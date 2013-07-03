#!/usr/bin/env python
#coding:utf-8
# Author:   Haiyang Peng
# Purpose:
# Created: 2013/7/02

from dbi import t_server
from dbi import session
from node import Server

class KeyWordException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Piece(Server):
    def __init__(self):
        self.knife = Knife()
    def breed(self):
        '''依据自身.dbid值，繁殖子节点：返回子嗣数量'''
        if not (self.childs is None) and len(self.childs)>0:
            return len(self.childs)
        result=session.query(t_server)
        for col, value in knife:
            #result = result.filter(t_server.:col == ":value")
            pass
        result = result.all()
        if result is None or len(result)==0:
            self.childs={}
            return 0
        for i in result:
            self.add_child(Server(i.id))
        return len(self.childs)

class Knife(object):
    def __init__(self,*keywords):
        self.words = self._all_words()
        self.knife = {}
        for i in keywords:
            if i in self.words.keys():
                self.knife[i] = self.words[i]
            else:
                raise KeyWordException(i)

    def _all_words(self):
        words = []
        words += self._get_word(t_server.region)
        words += self._get_word(t_server.product)
        words += self._get_word(t_server.role)
        words += self._get_word(t_server.dbms)
        words += self._get_word(t_server.vender)
        words += self._get_word(t_server.os_type)
        words += self._get_word(t_server.os_release)
        words += self._get_word(t_server.os_arch)
        words += [('reserve',t_server.is_reserve)]
        words = dict(words)
        return words

    def _get_word(self, col):
        ret = session.query(col).filter(col != None).distinct().all()
        return [ (str(x[0]),col) for x in ret ]


